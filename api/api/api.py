import logging
from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS

from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware

from .services import Token, Cache, Strategy, claim_native, claim_token, captcha_verify
from .const import NATIVE_TOKEN_ADDRESS


def is_token_enabled(address, tokens_list):
    if address.lower() == 'native':
        return True
    
    is_enabled = False
    checksum_address = Web3.to_checksum_address(address)
    for enabled_token in tokens_list:
        if checksum_address == enabled_token['address']:
            is_enabled = True
            break
    return is_enabled

def is_amount_valid(amount, token_address, tokens_list):

    if not token_address:
        raise ValueError(
            'Token address not supported',
            str(token_address),
            'supported tokens',
            " ".join(list(map(lambda x: x['address'], tokens_list)))
        ) 

    token_address_to_check = None
    if token_address.lower() == NATIVE_TOKEN_ADDRESS:
        token_address_to_check = NATIVE_TOKEN_ADDRESS
    else:
        token_address_to_check = Web3.to_checksum_address(token_address)

    for enabled_token in tokens_list:
        if token_address_to_check == enabled_token['address']:
            return (
                amount <= enabled_token['maximumAmount'],
                enabled_token['maximumAmount']
            )

    raise ValueError(
        'Token address not supported',
        token_address,
        'supported tokens',
        " ".join(list(map(lambda x: x['address'], tokens_list)))
    )


def get_balance(w3, address, format='ether'):
    balance = w3.eth.get_balance(address)
    return w3.from_wei(balance, format)


def setup_logger(log_level):
    # Set logger
    logging.basicConfig(level=log_level)


def print_info(w3, config):
    faucet_native_balance = get_balance(w3, config['FAUCET_ADDRESS'])
    logging.info("="*60)
    logging.info("RPC_URL        = " + config['FAUCET_RPC_URL'])
    logging.info("FAUCET ADDRESS = " + config['FAUCET_ADDRESS'])
    logging.info("FAUCET BALANCE = %d %s" % (faucet_native_balance, config['FAUCET_CHAIN_NAME']))
    logging.info("="*60)


def create_app():
    # Init Flask app
    app = Flask(__name__)
    app.config.from_object('api.settings')
    apiv1 = Blueprint("version1", "version1")
    # Apply CORS
    CORS(app, resources={r"/api/v1/*": {"origins": app.config['CORS_ALLOWED_ORIGINS']}})

    w3 = Web3(Web3.HTTPProvider(app.config['FAUCET_RPC_URL']))
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(app.config['FAUCET_PRIVATE_KEY']))

    cache = Cache(app.config['FAUCET_RATE_LIMIT_TIME_LIMIT_SECONDS'])

    setup_logger(logging.INFO)
    print_info(w3, app.config)

    @apiv1.route("/status")
    def status():
        return jsonify(status='ok'), 200
    

    @apiv1.route("/info")
    def info():
        return jsonify(
            enabledTokens=app.config['FAUCET_ENABLED_TOKENS'],
            chainId=app.config['FAUCET_CHAIN_ID'],
            chainName=app.config['FAUCET_CHAIN_NAME'],
            faucetAddress=app.config['FAUCET_ADDRESS']
        ), 200


    @apiv1.route("/ask", methods=["POST"])
    def ask():
        validation_errors = []

        request_data = request.get_json()

        # check hcatpcha
        catpcha_verified = captcha_verify(request_data.get('captcha'), app.config['CAPTCHA_VERIFY_ENDPOINT'], app.config['CAPTCHA_SECRET_KEY'])
        if not catpcha_verified:
            validation_errors.append('captcha: validation failed')
        
        if request_data.get('chainId') != app.config['FAUCET_CHAIN_ID']:
            validation_errors.append('chainId: %s is not supported %s' % (request_data.get('chainId'), app.config['FAUCET_CHAIN_ID']))
        
        recipient = request_data.get('recipient', None)
        if not w3.is_address(recipient):
            validation_errors.append('recipient: A valid recipient address must be specified')

        if not recipient or recipient.lower() == app.config['FAUCET_ADDRESS']:
            validation_errors.append('recipient: address cant\'t be the Faucet address itself')
        
        token_address = request_data.get('tokenAddress', None)
        if not token_address:
            validation_errors.append('tokenAddress: A valid token address or string \"native\" must be specified')
        
        try:
            if not is_token_enabled(token_address, app.config['FAUCET_ENABLED_TOKENS']):
                validation_errors.append('tokenAddress: Token %s is not enabled' % token_address)
        except:
            validation_errors.append('tokenAddress: invalid token address'), 400

        amount = request_data.get('amount', None)

        try:
            amount_valid, amount_limit = is_amount_valid(amount, token_address, app.config['FAUCET_ENABLED_TOKENS'])
            if not amount_valid:
                validation_errors.append('amount: a valid amount must be specified and must be less or equals to %s' % amount_limit)
        except ValueError as e:
            message = "".join([arg for arg in e.args])
            validation_errors.append(message)

        if len(validation_errors) > 0:
            return jsonify(errors=validation_errors), 400
        
        if app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.address.value:
            # Check last claim
            if cache.limit_by_address(recipient):
                return jsonify(errors=['recipient: you have exceeded the limit for today. Try again in %s hours' % cache.ttl(hours=True)]), 429
        elif app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.ip.value:
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            # Check last claim for the IP address
            if cache.limit_by_ip(ip_address):
                return jsonify(errors=['recipient: you have exceeded the limit for today. Try again in %s hours' % cache.ttl(hours=True)]), 429
        elif app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.ip_and_address:
            raise NotImplemented
        
        amount_wei = w3.to_wei(amount, 'ether')
        try:
            if token_address == 'native':
                tx_hash = claim_native(w3, app.config['FAUCET_ADDRESS'], recipient, amount_wei)
            else:
                tx_hash = claim_token(w3, app.config['FAUCET_ADDRESS'], recipient, amount_wei, token_address)
            return jsonify(transactionHash=tx_hash), 200
        except ValueError as e:
            message = "".join([arg['message'] for arg in e.args])
            return jsonify(errors=[message]), 400

    app.register_blueprint(apiv1, url_prefix="/api/v1")
    return app

import logging
from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS

from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware

from .services import Token, Cache, claim_native, claim_token, captcha_verify


def is_token_enabled(address, tokens_list):
    if address.lower() == 'native':
        return True
    
    is_enabled = False
    checksum_address = Web3.to_checksum_address(address)
    for enabled_tokens in tokens_list:
        if checksum_address == enabled_tokens['address']:
            is_enabled = True
            break
    return is_enabled


def create_app():
    # Init Flask app
    app = Flask(__name__)
    app.config.from_object('api.settings')
    apiv1 = Blueprint("version1", "version1")
    cors = CORS(app, resources={r"/api/v1/*": {"origins": app.config['CORS_ALLOWED_ORIGINS']}})

    w3 = Web3(Web3.HTTPProvider(app.config['FAUCET_RPC_URL']))
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(app.config['FAUCET_PRIVATE_KEY']))

    cache = Cache(app.config['FAUCET_TIME_LIMIST_SECONDS'])

    # Set logger
    logging.basicConfig(level=logging.INFO)
    logging.info("="*60)
    logging.info("RPC_URL        = " + app.config['FAUCET_RPC_URL'])
    logging.info("FAUCET ADDRESS = " + app.config['FAUCET_ADDRESS'])
    logging.info("="*60)


    @apiv1.route("/status")
    def status():
        return jsonify(status='ok'), 200
    

    @apiv1.route("/info")
    def info():
        enabled_tokens = []
        enabled_tokens.extend(app.config['FAUCET_ENABLED_TOKENS'])
        enabled_tokens.append(
            {
                'name': app.config['FAUCET_CHAIN_NATIVE_TOKEN_SYMBOL'],
                'address': 'native'
            }
        )
        return jsonify(
            enabledTokens=enabled_tokens,
            maximumAmount=app.config['FAUCET_AMOUNT'],
            chainId=app.config['FAUCET_CHAIN_ID']
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
        
        token_address = request_data.get('tokenAddress', None)
        if not token_address:
            validation_errors.append('tokenAddress: A valid token address or string \"native\" must be specified')
        
        try:
            if not is_token_enabled(token_address, app.config['FAUCET_ENABLED_TOKENS']):
                validation_errors.append('tokenAddress: Token %s is not enabled' % token_address)
        except:
            validation_errors.append('tokenAddress: invalid token address'), 400

        amount = request_data.get('amount', None)
        if not amount or float(amount) > app.config['FAUCET_AMOUNT']:
            validation_errors.append('amount: a valid amount must be specified and must be less or equals to %s' % app.config['FAUCET_AMOUNT'])

        if len(validation_errors) > 0:
            return jsonify(errors=validation_errors), 400
        
        # Check last claim
        if cache.limit_by_address(recipient):
            return jsonify(message='recipient: you have exceeded the limit for today. Try again in X hours'), 429
        
        amount_wei = w3.to_wei(amount, 'ether')
        try:
            if token_address == 'native':
                tx_hash = claim_native(w3, app.config['FAUCET_ADDRESS'], recipient, amount_wei)
            else:
                tx_hash = claim_token(w3, app.config['FAUCET_ADDRESS'], recipient, amount_wei, token_address)
            return jsonify(transactionHash=tx_hash), 200
        except ValueError as e:
            message = "".join([arg['message'] for arg in e.args])
            return jsonify(message=message), 400


    app.register_blueprint(apiv1, url_prefix="/api/v1")
    return app

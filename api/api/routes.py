from flask import Blueprint, current_app, jsonify, request
from web3 import Web3

from .services import (Strategy, Web3Singleton, captcha_verify, claim_native,
                       claim_token)
from .services.database import AccessKey
from .utils import is_amount_valid, is_token_enabled

apiv1 = Blueprint("version1", "version1")


@apiv1.route("/status")
def status():
    return jsonify(status='ok'), 200


@apiv1.route("/info")
def info():
    return jsonify(
        enabledTokens=current_app.config['FAUCET_ENABLED_TOKENS'],
        chainId=current_app.config['FAUCET_CHAIN_ID'],
        chainName=current_app.config['FAUCET_CHAIN_NAME'],
        faucetAddress=current_app.config['FAUCET_ADDRESS']
    ), 200


def _ask_route_validation(request_data, validate_captcha):
    validation_errors = []

    # Captcha validation
    if validate_captcha:
        # check hcatpcha
        catpcha_verified = captcha_verify(request_data.get('captcha'), current_app.config['CAPTCHA_VERIFY_ENDPOINT'], current_app.config['CAPTCHA_SECRET_KEY'])
        if not catpcha_verified:
            validation_errors.append('captcha: validation failed')

    if request_data.get('chainId') != current_app.config['FAUCET_CHAIN_ID']:
        validation_errors.append('chainId: %s is not supported. Supported chainId: %s' % (request_data.get('chainId'), current_app.config['FAUCET_CHAIN_ID']))

    recipient = request_data.get('recipient', None)
    if not Web3.is_address(recipient):
        validation_errors.append('recipient: A valid recipient address must be specified')

    if not recipient or recipient.lower() == current_app.config['FAUCET_ADDRESS']:
        validation_errors.append('recipient: address cant\'t be the Faucet address itself')

    token_address = request_data.get('tokenAddress', None)
    if not token_address:
        validation_errors.append('tokenAddress: A valid token address or string \"native\" must be specified')

    try:
        if not is_token_enabled(token_address, current_app.config['FAUCET_ENABLED_TOKENS']):
            validation_errors.append('tokenAddress: Token %s is not enabled' % token_address)
    except:
        validation_errors.append('tokenAddress: invalid token address'), 400

    amount = request_data.get('amount', None)

    try:
        amount_valid, amount_limit = is_amount_valid(amount, token_address, current_app.config['FAUCET_ENABLED_TOKENS'])
        if not amount_valid:
            validation_errors.append('amount: a valid amount must be specified and must be less or equals to %s' % amount_limit)
    except ValueError as e:
        message = "".join([arg for arg in e.args])
        validation_errors.append(message)

    return validation_errors, amount, recipient, token_address


def _ask(request_data, validate_captcha):
    validation_errors, amount, recipient, token_address = _ask_route_validation(request_data, validate_captcha)

    if len(validation_errors) > 0:
        return jsonify(errors=validation_errors), 400

    # Cache
    cache = current_app.config['FAUCET_CACHE']
    if current_app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.address.value:
        # Check last claim
        if cache.limit_by_address(recipient):
            return jsonify(errors=['recipient: you have exceeded the limit for today. Try again in %s hours' % cache.ttl(hours=True)]), 429
    elif current_app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.ip.value:
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        # Check last claim for the IP address
        if cache.limit_by_ip(ip_address):
            return jsonify(errors=['recipient: you have exceeded the limit for today. Try again in %s hours' % cache.ttl(hours=True)]), 429
    elif current_app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.ip_and_address:
        raise NotImplementedError

    amount_wei = Web3.to_wei(amount, 'ether')
    try:
        # convert to checksum address
        recipient = Web3.to_checksum_address(recipient)

        w3 = Web3Singleton(current_app.config['FAUCET_RPC_URL'], current_app.config['FAUCET_PRIVATE_KEY'])

        if token_address == 'native':
            tx_hash = claim_native(w3, current_app.config['FAUCET_ADDRESS'], recipient, amount_wei)
        else:
            tx_hash = claim_token(w3, current_app.config['FAUCET_ADDRESS'], recipient, amount_wei, token_address)
        return jsonify(transactionHash=tx_hash), 200
    except ValueError as e:
        message = "".join([arg['message'] for arg in e.args])
        return jsonify(errors=[message]), 400


@apiv1.route("/ask", methods=["POST"])
def ask():
    return _ask(request.get_json(), validate_captcha=True)


@apiv1.route("/cli/ask", methods=["POST"])
def cli_ask():
    access_key_id = request.headers.get('FAUCET_ACCESS_KEY_ID', None)
    secret_access_key = request.headers.get('FAUCET_SECRET_ACCESS_KEY', None)

    validation_errors = []

    if not access_key_id and not secret_access_key:
        validation_errors.append('Missing authentication headers')
        return jsonify(errors=validation_errors), 400

    # Fetch data from DB
    access_key = AccessKey.query.filter_by(access_key_id=access_key_id, secret_access_key=secret_access_key).first()

    if not access_key or not access_key.enabled:
        validation_errors.append('Access denied')
        return jsonify(errors=validation_errors), 403

    return _ask(request.get_json(), validate_captcha=False)

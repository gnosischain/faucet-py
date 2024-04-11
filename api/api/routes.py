from flask import Blueprint, current_app, jsonify, request
from web3 import Web3

from .const import FaucetRequestType, TokenType
from .services import (CSRF, AskEndpointValidator, Web3Singleton, claim_native,
                       claim_token)
from .services.database import AccessKey, Token, Transaction

apiv1 = Blueprint("version1", "version1")


@apiv1.route("/status")
def status():
    return jsonify(status='ok'), 200


@apiv1.route("/info", methods=["GET"])
def info():
    enabled_tokens = Token.enabled_tokens()
    rate_limit_days = current_app.config['FAUCET_RATE_LIMIT_TIME_LIMIT_SECONDS'] / (24*60*60)
    enabled_tokens_json = [
        {
            'address': t.address,
            'name': t.name,
            'maximumAmount': t.max_amount_day,
            'type': t.type,
            'rateLimitDays': round(rate_limit_days, 2)
        } for t in enabled_tokens
    ]

    # it's a singleton, gets instantiated at app creation time
    csrf = CSRF.instance
    csrf_item = csrf.generate_token()

    return jsonify(
        enabledTokens=enabled_tokens_json,
        chainId=current_app.config['FAUCET_CHAIN_ID'],
        chainName=current_app.config['FAUCET_CHAIN_NAME'],
        faucetAddress=current_app.config['FAUCET_ADDRESS'],
        csrfToken=csrf_item.token,
        csrfRequestId=csrf_item.request_id
    ), 200


def _ask(request_data, request_headers, validate_captcha=True, validate_csrf=True, access_key=None):
    """Process /ask request

    Args:
        request_data (object): request object
        validate_captcha (bool, optional): True if captcha must be validated, False otherwise. Defaults to True.
        validate_csrf (bool, optional): True if CSRF token must be validated, False otherwise. Defaults to True.
        access_key (object, optional): AccessKey instance. Defaults to None.

    Returns:
        tuple: json content, status code
    """
    validator = AskEndpointValidator(request_data,
                                     request_headers,
                                     validate_captcha,
                                     validate_csrf,
                                     access_key=access_key)
    ok = validator.validate()
    if not ok:
        return jsonify(errors=validator.errors), validator.http_return_code

    # convert amount to wei format
    amount_wei = Web3.to_wei(validator.amount, 'ether')
    try:
        # convert recipient address to checksum address
        recipient = Web3.to_checksum_address(validator.recipient)

        w3 = Web3Singleton(current_app.config['FAUCET_RPC_URL'],
                           current_app.config['FAUCET_PRIVATE_KEY'])

        if validator.token.type == TokenType.native.value:
            tx_hash = claim_native(w3,
                                   current_app.config['FAUCET_ADDRESS'],
                                   recipient,
                                   amount_wei)
        else:
            tx_hash = claim_token(w3, current_app.config['FAUCET_ADDRESS'],
                                  recipient,
                                  amount_wei,
                                  validator.token.address)

        # save transaction data on DB
        transaction = Transaction()
        transaction.hash = tx_hash
        transaction.recipient = recipient
        transaction.amount = validator.amount
        transaction.token = validator.token.address
        transaction.requester_ip = validator.ip_address
        if access_key:
            transaction.type = FaucetRequestType.cli.value
            transaction.access_key_id = access_key.access_key_id
        else:
            transaction.type = FaucetRequestType.web.value
        transaction.save()
        return jsonify(transactionHash=tx_hash), 200
    except ValueError as e:
        message = "".join([arg['message'] for arg in e.args])
        return jsonify(errors=[message]), 400


@apiv1.route("/ask", methods=["POST"])
def ask():
    data, status_code = _ask(request.get_json(), request.headers, validate_captcha=True, access_key=None)
    return data, status_code


@apiv1.route("/cli/ask", methods=["POST"])
def cli_ask():
    access_key_id = request.headers.get('X-faucet-access-key-id', None)
    secret_access_key = request.headers.get('X-faucet-secret-access-key', None)

    validation_errors = []

    if not access_key_id and not secret_access_key:
        validation_errors.append('Missing authentication headers')
        return jsonify(errors=validation_errors), 400

    # Fetch data from DB
    access_key = AccessKey.query.filter_by(access_key_id=access_key_id, secret_access_key=secret_access_key).first()

    if not access_key or not access_key.enabled:
        validation_errors.append('Access denied')
        return jsonify(errors=validation_errors), 403

    data, status_code = _ask(request.get_json(), request.headers, validate_captcha=False, validate_csrf=False, access_key=access_key)
    return data, status_code

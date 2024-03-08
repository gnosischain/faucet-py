from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from web3 import Web3

from .const import FaucetRequestType
from .services import (Strategy, Web3Singleton, captcha_verify, claim_native,
                       claim_token)
from .services.database import AccessKey, Token, Transaction

apiv1 = Blueprint("version1", "version1")


@apiv1.route("/status")
def status():
    return jsonify(status='ok'), 200


@apiv1.route("/info")
def info():
    enabled_tokens = Token.enabled_tokens()
    enabled_tokens_json = [
        {
            'address': t.address,
            'name': t.name,
            'maximumAmount': t.max_amount_day,
            'type': t.type
        } for t in enabled_tokens
    ]
    return jsonify(
        enabledTokens=enabled_tokens_json,
        chainId=current_app.config['FAUCET_CHAIN_ID'],
        chainName=current_app.config['FAUCET_CHAIN_NAME'],
        faucetAddress=current_app.config['FAUCET_ADDRESS']
    ), 200


def _ask_route_validation(request_data, validate_captcha=True):
    """Validate `ask/` endpoint request data

    Args:
        request_data (object): request object
        validate_captcha (bool, optional): True if captcha must be validated, False otherwise. Defaults to True.

    Returns:
        tuple: validation errors, amount, recipient, token address
    """
    validation_errors = []

    # Captcha validation
    if validate_captcha:
        # check hcatpcha
        catpcha_verified = captcha_verify(
            request_data.get('captcha'),
            current_app.config['CAPTCHA_VERIFY_ENDPOINT'], current_app.config['CAPTCHA_SECRET_KEY']
        )

        if not catpcha_verified:
            validation_errors.append('captcha: validation failed')

    if request_data.get('chainId') != current_app.config['FAUCET_CHAIN_ID']:
        validation_errors.append('chainId: %s is not supported. Supported chainId: %s' % (request_data.get('chainId'), current_app.config['FAUCET_CHAIN_ID']))

    recipient = request_data.get('recipient', None)
    if not Web3.is_address(recipient):
        validation_errors.append('recipient: A valid recipient address must be specified')

    if not recipient or recipient.lower() == current_app.config['FAUCET_ADDRESS']:
        validation_errors.append('recipient: address cant\'t be the Faucet address itself')

    amount = request_data.get('amount', None)
    token_address = request_data.get('tokenAddress', None)

    if token_address:
        try:
            # Clean up Token address
            if token_address.lower() != 'native':
                token_address = Web3.to_checksum_address(token_address)

            token = Token.query.with_entities(Token.enabled,Token.max_amount_day).filter_by(
                address=token_address,
                chain_id=request_data.get('chainId')).first()

            if token and token.enabled is True:
                if not amount:
                    validation_errors.append('amount: is required')
                if amount and amount > token.max_amount_day:
                    validation_errors.append('amount: a valid amount must be specified and must be less or equals to %s' % token[1])
                # except ValueError as e:
                #     message = "".join([arg for arg in e.args])
                #     validation_errors.append(message)
            else:
                validation_errors.append('tokenAddress: %s is not enabled' % token_address)
        except:
            validation_errors.append('tokenAddress: invalid token address'), 400
    else:
        validation_errors.append('tokenAddress: A valid token address or string \"native\" must be specified')
    return validation_errors, amount, recipient, token_address


def _ask(request_data, validate_captcha=True, access_key=None):
    """Process /ask request

    Args:
        request_data (object): request object
        validate_captcha (bool, optional): True if captcha must be validated, False otherwise. Defaults to True.
        access_key (object, optional): AccessKey instance. Defaults to None.

    Returns:
        tuple: json content, status code
    """
    validation_errors, amount, recipient, token_address = _ask_route_validation(request_data, validate_captcha)

    if len(validation_errors) > 0:
        return jsonify(errors=validation_errors), 400

    ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

    if current_app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.address.value:
        # Check last claim by recipient
        transaction = Transaction.last_by_recipient(recipient)
    elif current_app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.ip.value:
        # Check last claim by IP
        transaction = Transaction.last_by_ip(ip_address)
    elif current_app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.ip_and_address.value:
        transaction = Transaction.last_by_ip_and_recipient(ip_address,
                                                           recipient)
    elif current_app.config['FAUCET_RATE_LIMIT_STRATEGY'].strategy == Strategy.ip_or_address.value:
        transaction = Transaction.last_by_ip_or_recipient(ip_address,
                                                          recipient)
    else:
        raise NotImplementedError

    # Check if the recipient can claim funds, they must not have claimed any tokens 
    # in the period of time defined by FAUCET_RATE_LIMIT_TIME_LIMIT_SECONDS
    if transaction:
        time_diff_seconds = (datetime.utcnow() - transaction.created).total_seconds()
        if time_diff_seconds < current_app.config['FAUCET_RATE_LIMIT_TIME_LIMIT_SECONDS']:
            time_diff_hours = 24-(time_diff_seconds/(24*60))
            return jsonify(errors=['recipient: you have exceeded the limit for today. Try again in %d hours' % time_diff_hours]), 429

    # convert amount to wei format
    amount_wei = Web3.to_wei(amount, 'ether')
    try:
        # convert recipient address to checksum address
        recipient = Web3.to_checksum_address(recipient)

        w3 = Web3Singleton(current_app.config['FAUCET_RPC_URL'], current_app.config['FAUCET_PRIVATE_KEY'])

        token = Token.get_by_address(token_address)
        if token.type == 'native':
            tx_hash = claim_native(w3, current_app.config['FAUCET_ADDRESS'], recipient, amount_wei)
        else:
            tx_hash = claim_token(w3, current_app.config['FAUCET_ADDRESS'], recipient, amount_wei, token_address)
        
        # save transaction data on DB
        transaction = Transaction()
        transaction.hash = tx_hash
        transaction.recipient = recipient
        transaction.amount = amount
        transaction.token = token_address
        transaction.requester_ip = ip_address
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
    data, status_code = _ask(request.get_json(), validate_captcha=True, access_key=None)
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

    data, status_code = _ask(request.get_json(), validate_captcha=False, access_key=access_key)
    return data, status_code

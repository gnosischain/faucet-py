from flask import Blueprint, current_app, jsonify, request
from web3 import Web3

from .services import (Strategy, Web3Singleton, captcha_verify, claim_native,
                       claim_token)
from .services.database import AccessKey, Token, Transaction
# from .utils import is_amount_valid, is_token_enabled

apiv1 = Blueprint("version1", "version1")


@apiv1.route("/status")
def status():
    return jsonify(status='ok'), 200


@apiv1.route("/info")
def info():
    enabled_tokens = Token.query.with_entities(Token.name, Token.address,
                                               Token.chain_id).filter_by(enabled=True).all()
    return jsonify(
        enabledTokens=enabled_tokens,
        # chainId=current_app.config['FAUCET_ENABLED_CHAIN_IDS'],
        # chainName=current_app.config['FAUCET_CHAIN_NAME'],
        faucetAddress=current_app.config['FAUCET_ADDRESS']
    ), 200


def _ask_route_validation(request_data, validate_captcha):
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

    if request_data.get('chainId') not in current_app.config['FAUCET_ENABLED_CHAIN_IDS']:
        validation_errors.append('chainId: %s is not supported. Supported chainIds: %s' % (
                request_data.get('chainId'),
                ', '.join([str(x) for x in current_app.config['FAUCET_ENABLED_CHAIN_IDS']])
            )
        )

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

            if token and token[0] is True:
                if not amount:
                    validation_errors.append('amount: is required')
                if amount and amount > token[1]:
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
        
        # save info on DB
        transaction = Transaction()
        transaction.hash = tx_hash
        transaction.recipient = recipient
        transaction.amount = amount
        transaction.token = token_address
        transaction.save()
        return jsonify(transactionHash=tx_hash), 200
    except ValueError as e:
        message = "".join([arg['message'] for arg in e.args])
        return jsonify(errors=[message]), 400


@apiv1.route("/ask", methods=["POST"])
def ask():
    data, status_code = _ask(request.get_json(), validate_captcha=True)
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

    data, status_code = _ask(request.get_json(), validate_captcha=False)
    return data, status_code

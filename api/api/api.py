import logging
from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS

from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware

from .services import Token, Cache, claim_native, claim_token


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
        return jsonify(
            enabledTokens=app.config['FAUCET_ENABLED_TOKENS'],
            maximumAmount=app.config['FAUCET_AMOUNT']), 200


    @apiv1.route("/ask", methods=["POST"])
    def ask():
        validation_errors = []

        request_data = request.get_json()
        if request_data.get('chainId') != app.config['FAUCET_CHAIN_ID']:
            validation_errors.append('chainId: %s is not supported %s' % (request_data.get('chainId'), app.config['FAUCET_CHAIN_ID']))
        
        recipient = request_data.get('recipient', None)
        if not recipient:
            validation_errors.append('recipient: A valid recipient address must be specified')
        
        token_address = request_data.get('tokenAddress', None)
        if not token_address:
            validation_errors.append('tokenAddress: A valid token address or string \"native\" must be specified')
        
        try:
            if token_address and (
                token_address.lower() != 'native' and not Web3.to_checksum_address(token_address) in app.config['FAUCET_ENABLED_TOKENS']
            ):
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
        
        if token_address == 'native':
            tx_hash = claim_native(w3, app.config['FAUCET_ADDRESS'], recipient, amount)
        else:
            tx_hash = claim_token(w3, app.config['FAUCET_ADDRESS'], recipient, amount, token_address)
        return jsonify(transactionHash=tx_hash), 200


    app.register_blueprint(apiv1, url_prefix="/api/v1")
    return app

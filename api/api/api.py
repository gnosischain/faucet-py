import logging

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from .manage import create_access_keys_cmd
from .routes import apiv1
from .services import Web3Singleton
from .services.database import db


def setup_logger(log_level):
    # Set logger
    logging.basicConfig(level=log_level)


def setup_cors(app):
    # Apply CORS
    CORS(app, resources={r"/api/v1/*": {"origins": app.config['CORS_ALLOWED_ORIGINS']}})


def print_info(w3, config):
    faucet_native_balance = w3.eth.get_balance(config['FAUCET_ADDRESS'])
    logging.info("=" * 60)
    logging.info("RPC_URL        = " + config['FAUCET_RPC_URL'])
    logging.info("FAUCET ADDRESS = " + config['FAUCET_ADDRESS'])
    logging.info("FAUCET BALANCE = %d %s" % (w3.from_wei(faucet_native_balance, 'ether'), config['FAUCET_CHAIN_NAME']))
    logging.info("=" * 60)


def create_app():
    # Init Flask app
    app = Flask(__name__)
    # Initialize main settings
    app.config.from_object('api.settings')
    # Initialize API Routes
    app.register_blueprint(apiv1, url_prefix="/api/v1")
    # Add cli commands
    app.cli.add_command(create_access_keys_cmd)

    with app.app_context():
        db.init_app(app)
        Migrate(app, db)

    # Initialize Web3 class for latter usage
    w3 = Web3Singleton(app.config['FAUCET_RPC_URL'], app.config['FAUCET_PRIVATE_KEY'])

    setup_cors(app)
    setup_logger(logging.INFO)
    print_info(w3, app.config)
    return app

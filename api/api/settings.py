import json
import os

from dotenv import load_dotenv
from eth_account import Account
from eth_account.signers.local import LocalAccount

from .const import CHAIN_NAMES
from .services import RateLimitStrategy

# from .utils import get_chain_name

load_dotenv()

rate_limit_strategy = RateLimitStrategy()
rate_limit_strategy.strategy = os.getenv('FAUCET_RATE_LIMIT_STRATEGY', default=rate_limit_strategy.default_strategy)

FAUCET_RPC_URL = os.getenv("FAUCET_RPC_URL")
FAUCET_PRIVATE_KEY = os.environ.get("FAUCET_PRIVATE_KEY")
FAUCET_CHAIN_ID = int(os.getenv('FAUCET_CHAIN_ID'))
FAUCET_CHAIN_NAME = CHAIN_NAMES[FAUCET_CHAIN_ID]
FAUCET_ADDRESS: LocalAccount = Account.from_key(FAUCET_PRIVATE_KEY).address
FAUCET_RATE_LIMIT_STRATEGY = rate_limit_strategy
FAUCET_RATE_LIMIT_TIME_LIMIT_SECONDS = int(os.getenv('FAUCET_RATE_LIMIT_TIME_LIMIT_SECONDS', 86400))  # 86400 = 24h

SQLALCHEMY_DATABASE_URI = os.getenv('FAUCET_DATABASE_URI')

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '*')

CAPTCHA_VERIFY_ENDPOINT = os.getenv('CAPTCHA_VERIFY_ENDPOINT')
CAPTCHA_SECRET_KEY = os.getenv('CAPTCHA_SECRET_KEY')

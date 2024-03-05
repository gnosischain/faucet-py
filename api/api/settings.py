import json
import os

from dotenv import load_dotenv
from eth_account import Account
from eth_account.signers.local import LocalAccount

from .services import RateLimitStrategy
from .utils import get_chain_name

load_dotenv()

rate_limit_strategy = RateLimitStrategy()
rate_limit_strategy.strategy = os.getenv('FAUCET_RATE_LIMIT_STRATEGY', default=rate_limit_strategy.default_strategy)

FAUCET_RPC_URL = os.getenv("FAUCET_RPC_URL")
FAUCET_PRIVATE_KEY = os.environ.get("FAUCET_PRIVATE_KEY")
FAUCET_CHAIN_ID = os.getenv('FAUCET_CHAIN_ID')
FAUCET_CHAIN_NAME = get_chain_name(os.getenv('FAUCET_CHAIN_ID'))

SQLALCHEMY_DATABASE_URI = os.getenv('FAUCET_DATABASE_URI')

# env FAUCET_ENABLED_TOKENS
# sample JSON string:
# [
#     {
#         "address": "0x19C653Da7c37c66208fbfbE8908A5051B57b4C70"
#         "name": "GNO",
#         "maximumAmount": 0.5
#     }
# ]
FAUCET_ENABLED_TOKENS = json.loads(os.getenv('FAUCET_ENABLED_TOKENS', default='[]'))
FAUCET_ADDRESS: LocalAccount = Account.from_key(FAUCET_PRIVATE_KEY).address
FAUCET_RATE_LIMIT_STRATEGY = rate_limit_strategy
FAUCET_RATE_LIMIT_TIME_LIMIT_SECONDS = int(os.getenv('FAUCET_RATE_LIMIT_TIME_LIMIT_SECONDS', 86400))  # 86400 = 24h

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '*')

CAPTCHA_VERIFY_ENDPOINT = os.getenv('CAPTCHA_VERIFY_ENDPOINT')
CAPTCHA_SECRET_KEY = os.getenv('CAPTCHA_SECRET_KEY')
import os

from dotenv import load_dotenv
from eth_account import Account
from eth_account.signers.local import LocalAccount

from .const import CHAIN_NAMES, ClaimValidationType
from .services import RateLimitStrategy

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
CAPTCHA_SITE_KEY = os.getenv('CAPTCHA_SITE_KEY')

CSRF_PRIVATE_KEY = os.getenv('CSRF_PRIVATE_KEY')
CSRF_SECRET_SALT = os.getenv('CSRF_SECRET_SALT')

# Domain that is allowed as external sources to validate "faucet claims".
# Users have to post a message on the allowed website/domain and the text must contain
# the recipient address.
# CLAIM_VALIDATION_DISCOURSE_API_URL = None
# CLAIM_VALIDATION_ALLOWED_WEBSITE = None
# CLAIM_VALIDATION_WEBSITE_TYPE = None

CLAIM_VALIDATION_ENABLED = os.getenv('CLAIM_VALIDATION_ENABLED', 'True') in ('True', 'true', '1')
if CLAIM_VALIDATION_ENABLED:
    CLAIM_VALIDATION_ALLOWED_WEBSITE = os.getenv('CLAIM_VALIDATION_ALLOWED_WEBSITE')
    CLAIM_VALIDATION_WEBSITE_TYPE = os.getenv('CLAIM_VALIDATION_WEBSITE_TYPE',
                                              ClaimValidationType.discourse.value)

    if CLAIM_VALIDATION_WEBSITE_TYPE == ClaimValidationType.discourse.value:
        CLAIM_VALIDATION_DISCOURSE_API_URL = os.getenv('CLAIM_VALIDATION_DISCOURSE_API_URL')

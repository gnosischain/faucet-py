import os
import json
from dotenv import load_dotenv
from eth_account import Account
from eth_account.signers.local import LocalAccount


load_dotenv()

FAUCET_RPC_URL = os.getenv("FAUCET_RPC_URL")
FAUCET_PRIVATE_KEY = os.environ.get("FAUCET_PRIVATE_KEY")
FAUCET_CHAIN_ID=os.getenv('FAUCET_CHAIN_ID')
FAUCET_ENABLED_TOKENS=json.loads(os.getenv('FAUCET_ENABLED_TOKENS', default='[]'))
FAUCET_AMOUNT=float(os.getenv('FAUCET_AMOUNT'))
FAUCET_ADDRESS: LocalAccount = Account.from_key(FAUCET_PRIVATE_KEY).address
FAUCET_TIME_LIMIST_SECONDS=seconds=os.getenv('FAUCET_TIME_LIMIST_SECONDS', 86400) # 86400 = 24h
CORS_ALLOWED_ORIGINS=os.getenv('CORS_ALLOWED_ORIGINS', '*')
CAPTCHA_VERIFY_ENDPOINT=os.getenv('CAPTCHA_VERIFY_ENDPOINT')
CAPTCHA_SECRET_KEY=os.getenv('CAPTCHA_SECRET_KEY')
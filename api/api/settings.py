import os
from dotenv import load_dotenv
from eth_account import Account
from eth_account.signers.local import LocalAccount


load_dotenv()

FAUCET_RPC_URL = os.getenv("FAUCET_RPC_URL")
FAUCET_PRIVATE_KEY = os.environ.get("FAUCET_PRIVATE_KEY")
FAUCET_CHAIN_ID=os.getenv('FAUCET_CHAIN_ID')
FAUCET_ENABLED_TOKENS=os.getenv('FAUCET_ENABLED_TOKENS', default=None) and os.getenv('FAUCET_ENABLED_TOKENS').split(',') or []
FAUCET_AMOUNT=float(os.getenv('FAUCET_AMOUNT'))
FAUCET_ADDRESS: LocalAccount = Account.from_key(FAUCET_PRIVATE_KEY).address
FAUCET_TIME_LIMIST_SECONDS=seconds=os.getenv('FAUCET_TIME_LIMIST_SECONDS', 86400) # 86400 = 24h
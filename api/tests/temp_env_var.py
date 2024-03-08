from secrets import token_bytes

from api.const import (DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
                       DEFAULT_NATIVE_MAX_AMOUNT_PER_DAY, NATIVE_TOKEN_ADDRESS,
                       TokenType)

ERC20_TOKEN_ADDRESS = "0x" + '1' * 40

CAPTCHA_TEST_SECRET_KEY = '0x0000000000000000000000000000000000000000'
CAPTCHA_TEST_RESPONSE_TOKEN = '10000000-aaaa-bbbb-cccc-000000000001'

FAUCET_CHAIN_ID = 10200

FAUCET_ENABLED_TOKENS = [
    {
        "address": NATIVE_TOKEN_ADDRESS,
        "name": "Native",
        "maximumAmount": DEFAULT_NATIVE_MAX_AMOUNT_PER_DAY,
        "chainId": FAUCET_CHAIN_ID,
        "type": TokenType.native.value
    },
    {
        "address": ERC20_TOKEN_ADDRESS,
        "name": "TestToken",
        "maximumAmount": DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
        "chainId": FAUCET_CHAIN_ID,
        "type": TokenType.erc20.value
    }
]

TEMP_ENV_VARS = {
    'FAUCET_RPC_URL': 'http://localhost:8545',
    'FAUCET_CHAIN_ID': str(FAUCET_CHAIN_ID),
    'FAUCET_PRIVATE_KEY': token_bytes(32).hex(),
    'FAUCET_RATE_LIMIT_TIME_LIMIT_SECONDS': '10',
    'FAUCET_DATABASE_URI': 'sqlite://',  # run in-memory
    'CAPTCHA_SECRET_KEY': CAPTCHA_TEST_SECRET_KEY
}

# Mocked values
NATIVE_TRANSFER_TX_HASH = '0x3a1a19c3bfd5fbb7ae358b818ea066c7020e932e7f5a81d0aebe75e07d198adc'
TOKEN_TRANSFER_TX_HASH = '0xe48e9d60880a7000aa27216c08f8cb4983e3c2c6f93b6c926983231cb0c71df1'

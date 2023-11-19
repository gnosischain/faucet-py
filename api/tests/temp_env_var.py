from secrets import token_bytes


TEMP_ENV_VARS = {
    'FAUCET_RPC_URL': 'http://localhost:8545',
    'FAUCET_CHAIN_ID': '100000',
    'FAUCET_PRIVATE_KEY': token_bytes(32).hex(),
    'FAUCET_AMOUNT': 0.1,
    'FAUCET_TIME_LIMIST_SECONDS': '1',
    'FAUCET_ENABLED_TOKENS': ['0x' + '0'*40]
}

# Mocked values
NATIVE_TRANSFER_TX_HASH = '0x3a1a19c3bfd5fbb7ae358b818ea066c7020e932e7f5a81d0aebe75e07d198adc'
TOKEN_TRANSFER_TX_HASH = '0xe48e9d60880a7000aa27216c08f8cb4983e3c2c6f93b6c926983231cb0c71df1'
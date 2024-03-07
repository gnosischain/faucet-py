from enum import Enum

NATIVE_TOKEN_ADDRESS = 'native'
DEFAULT_NATIVE_MAX_AMOUNT_PER_DAY = 0.01
DEFAULT_ERC20_MAX_AMOUNT_PER_DAY = 0.01

CHAIN_NAMES = {
    1: 'ETHEREUM MAINNET',
    100: 'GNOSIS CHAIN',
    10200: 'CHIADO CHAIN'
}


class FaucetRequestType(Enum):
    web = 'web'
    cli = 'cli'

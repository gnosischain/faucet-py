from enum import Enum

ZERO_ADDRESS = "0x" + '0' * 40
NATIVE_TOKEN_ADDRESS = ZERO_ADDRESS
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


class TokenType(Enum):
    native = 'native'
    erc20 = 'erc20'

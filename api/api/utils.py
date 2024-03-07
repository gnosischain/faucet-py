import secrets

from web3 import Web3

from .const import NATIVE_TOKEN_ADDRESS


def get_chain_name(chain_id):
    chains = {
        1: 'Ethereum',
        100: 'Gnosis Chain',
        10200: 'Chiado Chain Testnet'
    }

    return chains.get(int(chain_id), 'Undefined')


def is_token_enabled(address, tokens_list):
    # Native token enabled by default
    if address.lower() == 'native':
        return True

    is_enabled = False
    checksum_address = Web3.to_checksum_address(address)
    for enabled_token in tokens_list:
        if checksum_address == enabled_token['address']:
            is_enabled = True
            break
    return is_enabled


def is_amount_valid(amount, token_address, tokens_list):

    if not token_address:
        raise ValueError(
            'Token address not supported',
            str(token_address),
            'supported tokens',
            " ".join(list(map(lambda x: x['address'], tokens_list)))
        )

    token_address_to_check = None
    if token_address.lower() == NATIVE_TOKEN_ADDRESS:
        token_address_to_check = NATIVE_TOKEN_ADDRESS
    else:
        token_address_to_check = Web3.to_checksum_address(token_address)

    for enabled_token in tokens_list:
        if token_address_to_check == enabled_token['address']:
            return (
                amount <= enabled_token['maximumAmount'],
                enabled_token['maximumAmount']
            )

    raise ValueError(
        'Token address not supported',
        token_address,
        'supported tokens',
        " ".join(list(map(lambda x: x['address'], tokens_list)))
    )


def generate_access_key():
    access_key_id = secrets.token_hex(8)  # returns a 16 chars long string
    secret_access_key = secrets.token_hex(16)  # returns a 32 chars long string
    return access_key_id, secret_access_key

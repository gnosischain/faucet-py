import secrets


def get_chain_name(chain_id):
    chains = {
        1: 'Ethereum',
        100: 'Gnosis Chain',
        10200: 'Chiado Chain Testnet'
    }

    return chains.get(int(chain_id), 'Undefined')


def generate_access_key():
    access_key_id = secrets.token_hex(8)  # returns a 16 chars long string
    secret_access_key = secrets.token_hex(16)  # returns a 32 chars long string
    return access_key_id, secret_access_key

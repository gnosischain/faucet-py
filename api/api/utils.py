def get_chain_name(chain_id):
    chains = {
        1: 'Ethereum',
        100: 'Gnosis Chain',
        10200: 'Chiado Chain Testnet'
    }

    return chains.get(int(chain_id), 'Undefined')
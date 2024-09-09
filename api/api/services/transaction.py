from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware

from .token import Token


class Web3Instance:
    def __init__(self, faucet_rpc_url, faucet_private_key):
        self.w3 = Web3(Web3.HTTPProvider(faucet_rpc_url))
        self.w3.middleware_onion.add(construct_sign_and_send_raw_middleware(faucet_private_key))


class Web3Singleton:
    _instance = None

    def __new__(cls, faucet_rpc_url, faucet_private_key):
        if not hasattr(cls, 'instance'):
            cls.instance = Web3Instance(faucet_rpc_url, faucet_private_key)
        return cls.instance.w3


def claim_native(w3, sender, recipient, amount):
    """
    Claim Native tokens.
    args:
    - w3: instance of Web3
    - sender: String
    - recipient: String
    - amount: integer in wei format
    """

    nonce = w3.eth.get_transaction_count(sender)

    tx_dict = {
        'from': sender,
        'to': recipient,
        'value': amount,
        'nonce': nonce
    }
    
    tx_hash = w3.eth.send_transaction(tx_dict).hex()

    # this may cause a timeout, keep here for testing purposes
    # receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    # if receipt.status == 1:
    #     print(f"transaction successful {tx_hash}")
    # else:
    #     print(f"transaction failed {tx_hash}")

    return tx_hash


def claim_token(w3, sender, recipient, amount, token_address):
    """
    Claim ERC20 Tokens.
    args:
    - w3: instance of Web3
    - sender: String
    - recipient: String
    - amount: integer in wei format
    - token_address: String
    """
    token = Token(token_address, w3)
    return token.transfer(sender, recipient, amount)

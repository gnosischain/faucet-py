from .token import Token


def claim_native(w3, sender, recipient, amount):
    """
    Claim Native tokens.
    args:
    - w3: instance of Web3
    - sender: String
    - recipient: String
    - amount: integer in wei format
    """
    tx_dict = {
        'from': sender,
        'to': recipient,
        'value': amount
    }
    return w3.eth.send_transaction(tx_dict).hex()

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
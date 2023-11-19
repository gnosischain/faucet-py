from .token import Token


def claim_native(w3, sender, recipient, amount):
    tx_dict = {
        'from': sender,
        'to': recipient,
        'amount': amount
    }
    return w3.eth.send_transaction(tx_dict)

def claim_token(w3, sender, recipient, amount, token_address):
    token = Token(token_address, w3)
    tx_hash = token.transfer(sender, recipient, amount)
    return tx_hash
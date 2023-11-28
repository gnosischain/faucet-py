import os
import json


class Token:
    def __init__(self, address, w3) -> None:
        self.address = address
        self.erc20_abi = self._load_abi()
        self.w3 = w3
        self.contract = w3.eth.contract(self.address, abi=self.erc20_abi)

    def _load_abi(self):
        erc20_filepath = os.path.join(os.path.dirname(__file__), "../ABI/erc20.json")
        with open(erc20_filepath, "r") as file:
            return json.load(file)
        
    def transfer(self, sender_address, recipient_address, amount_wei):
        transfer_tx = self.contract.functions.transfer(
            recipient_address,
            amount_wei
        ).build_transaction({
            'from': sender_address
        })

        tx_hash = self.w3.eth.send_transaction(transfer_tx)
        return tx_hash.hex()
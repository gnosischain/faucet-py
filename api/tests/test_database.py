from conftest import BaseTest
from temp_env_var import NATIVE_TRANSFER_TX_HASH, NATIVE_TOKEN_ADDRESS, ZERO_ADDRESS

from api.services.database import AccessKey, Transaction, Token
from api.utils import generate_access_key


class TestDatabase(BaseTest):

    def test_access_keys(self, client):
        access_key_id, secret_access_key = generate_access_key()
        assert len(access_key_id) == 16
        assert len(secret_access_key) == 32
        access_key = AccessKey()
        access_key.access_key_id = access_key_id
        access_key.secret_access_key = secret_access_key
        access_key.save()
        result = AccessKey.query.filter_by(access_key_id=access_key_id, secret_access_key=secret_access_key).all()
        assert len(result) == 1  # we just have 1 item for that key ID and access key
        assert result[0].access_key_id == access_key_id
        assert result[0].secret_access_key == secret_access_key
        assert result[0].enabled is True

    def test_transactions(self, client):
        token = Token.get_by_address(NATIVE_TOKEN_ADDRESS)

        transaction = Transaction()
        transaction.hash = NATIVE_TRANSFER_TX_HASH
        transaction.recipient = ZERO_ADDRESS
        transaction.amount = 1
        transaction.token = token.address
        transaction.requester_ip = '192.168.0.1'
        transaction.save()

        transaction = Transaction()
        transaction.hash = NATIVE_TRANSFER_TX_HASH
        transaction.recipient = ZERO_ADDRESS
        transaction.amount = 1
        transaction.token = token.address
        transaction.requester_ip = '192.168.0.1'
        transaction.save()

import pytest
from conftest import BaseTest
from sqlalchemy.exc import IntegrityError
from temp_env_var import NATIVE_TOKEN_ADDRESS, NATIVE_TRANSFER_TX_HASH

from api.const import ZERO_ADDRESS
from api.services.database import (AccessKey, AccessKeyConfig, Token,
                                   Transaction)
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

        # Duplicates for secret_access_key are not allowed
        with pytest.raises(IntegrityError):
            access_key_id2, _ = generate_access_key()
            access_key = AccessKey()
            access_key.access_key_id = access_key_id2
            access_key.secret_access_key = secret_access_key
            access_key.save()

    def test_access_key_config(self, client):
        access_key_id, secret_access_key = generate_access_key()
        access_key = AccessKey()
        access_key.access_key_id = access_key_id
        access_key.secret_access_key = secret_access_key
        access_key.save()

        config = AccessKeyConfig()
        config.access_key_id = access_key.access_key_id
        config.chain_id = 10200
        config.erc20_max_amount_day = 10
        config.native_max_amount_day = 20
        config.save()

        # Duplicates for (access_key_id, chain_id) are not allowed
        with pytest.raises(IntegrityError):
            config = AccessKeyConfig()
            config.access_key_id = access_key.access_key_id
            config.chain_id = 10200
            config.erc20_max_amount_day = 5
            config.native_max_amount_day = 10
            config.save()

    def test_transactions(self, client):
        token = Token.get_by_address(NATIVE_TOKEN_ADDRESS)

        transaction = Transaction()
        transaction.hash = NATIVE_TRANSFER_TX_HASH
        transaction.recipient = ZERO_ADDRESS
        transaction.amount = 1
        transaction.token = token.address
        transaction.requester_ip = '192.168.0.1'
        transaction.save()

        # Duplicates for tx hash are not allowed
        with pytest.raises(IntegrityError):
            transaction = Transaction()
            transaction.hash = NATIVE_TRANSFER_TX_HASH
            transaction.recipient = ZERO_ADDRESS
            transaction.amount = 1
            transaction.token = token.address
            transaction.requester_ip = '192.168.0.1'
            transaction.save()

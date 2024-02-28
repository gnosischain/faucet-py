from conftest import BaseTest
# from mock import patch
from temp_env_var import (CAPTCHA_TEST_RESPONSE_TOKEN, ERC20_TOKEN_ADDRESS,
                          ERC20_TOKEN_AMOUNT, NATIVE_TOKEN_ADDRESS,
                          NATIVE_TOKEN_AMOUNT, NATIVE_TRANSFER_TX_HASH,
                          TEMP_ENV_VARS, TOKEN_TRANSFER_TX_HASH, ZERO_ADDRESS)

from api.services.database import AccessKey
from api.utils import generate_access_key


class TestDatabase(BaseTest):
    def test_models(self, client):
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

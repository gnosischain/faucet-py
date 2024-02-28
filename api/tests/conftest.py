import os

import pytest
from flask_migrate import upgrade
from temp_env_var import (CAPTCHA_TEST_RESPONSE_TOKEN, ERC20_TOKEN_ADDRESS,
                          ERC20_TOKEN_AMOUNT, NATIVE_TOKEN_ADDRESS,
                          NATIVE_TOKEN_AMOUNT, NATIVE_TRANSFER_TX_HASH,
                          TEMP_ENV_VARS, TOKEN_TRANSFER_TX_HASH, ZERO_ADDRESS)

from api import create_app

api_prefix = '/api/v1'


class BaseTest:
    def _mock(self, mocker, env_variables=None):
        # Mock values
        mocker.patch('api.routes.claim_native', return_value=NATIVE_TRANSFER_TX_HASH)
        mocker.patch('api.routes.claim_token', return_value=TOKEN_TRANSFER_TX_HASH)
        mocker.patch('api.routes.captcha_verify', return_value=True)
        mocker.patch('api.api.print_info', return_value=None)
        if env_variables:
            mocker.patch.dict(os.environ, env_variables)
        return mocker

    def _create_app(self):
        return create_app()

    @pytest.fixture
    def app(self, mocker):
        mocker = self._mock(mocker, TEMP_ENV_VARS)
        app = self._create_app()
        with app.app_context():
            upgrade()
            yield app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

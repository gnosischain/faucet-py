import os

import pytest
from temp_env_var import (FAUCET_ENABLED_TOKENS, NATIVE_TRANSFER_TX_HASH,
                          TEMP_ENV_VARS, TOKEN_TRANSFER_TX_HASH)

from api import create_app
from api.services import Strategy
from api.services.database import Token, db

api_prefix = '/api/v1'


class BaseTest:
    def _mock(self, mocker, env_variables=None):
        # Mock values
        mocker.patch('api.routes.claim_native', return_value=NATIVE_TRANSFER_TX_HASH)
        mocker.patch('api.routes.claim_token', return_value=TOKEN_TRANSFER_TX_HASH)
        mocker.patch('api.services.captcha_verify', return_value=True)
        mocker.patch('api.api.print_info', return_value=None)
        if env_variables:
            mocker.patch.dict(os.environ, env_variables)
        return mocker

    def _create_app(self):
        return create_app()

    def _reset_db(self):
        print("#== Reset DB ==#")
        db.drop_all()
        db.create_all()
        self.populate_db()

    @pytest.fixture
    def app(self, mocker):
        mocker = self._mock(mocker, TEMP_ENV_VARS)
        app = self._create_app()
        with app.app_context():
            self._reset_db()
            yield app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def populate_db(self):
        for enabled_token in FAUCET_ENABLED_TOKENS:
            token = Token()
            token.address = enabled_token['address']
            token.name = enabled_token['name']
            token.chain_id = enabled_token['chainId']
            token.max_amount_day = enabled_token['maximumAmount']
            token.type = enabled_token['type']
            token.save()


class RateLimitIPBaseTest(BaseTest):
    @pytest.fixture
    def app(self, mocker):
        # Set rate limit strategy to IP
        env_vars = TEMP_ENV_VARS.copy()
        env_vars['FAUCET_RATE_LIMIT_STRATEGY'] = Strategy.ip.value
        mocker = self._mock(mocker, env_vars)

        app = self._create_app()
        with app.app_context():
            self._reset_db()
            yield app


class RateLimitIPorAddressBaseTest(BaseTest):
    @pytest.fixture
    def app(self, mocker):
        # Set rate limit strategy to IP
        env_vars = TEMP_ENV_VARS.copy()
        env_vars['FAUCET_RATE_LIMIT_STRATEGY'] = Strategy.ip_or_address.value
        mocker = self._mock(mocker, env_vars)

        app = self._create_app()
        with app.app_context():
            self._reset_db()
            yield app

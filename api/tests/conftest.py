import os
from unittest import TestCase, TestResult, mock

from flask.testing import FlaskClient

from api import create_app
from api.services import Strategy
from api.services.database import Token, db

from .temp_env_var import FAUCET_ENABLED_TOKENS, TEMP_ENV_VARS

api_prefix = '/api/v1'


class BaseTest(TestCase):

    def mock_claim_native(self, *args):
        tx_hash = '0x0' + '%d' % self.native_tx_counter * 63
        self.native_tx_counter += 1
        return tx_hash

    def mock_claim_erc20(self, *args):
        tx_hash = '0x1' + '%d' % self.erc20_tx_counter * 63
        self.erc20_tx_counter += 1
        return tx_hash

    def _mock(self, env_variables=None):
        # Mock values
        self.patchers = [
            mock.patch('api.routes.claim_native', self.mock_claim_native),
            mock.patch('api.routes.claim_token', self.mock_claim_erc20),
            mock.patch('api.services.captcha_verify', return_value=True),
            mock.patch('api.api.print_info', return_value=None)
        ]
        if env_variables:
            self.patchers.append(mock.patch.dict(os.environ, env_variables))
   
        for p in self.patchers:
            p.start()

    def _reset_db(self):
        print("#== Reset DB ==#")
        db.drop_all()
        db.create_all()
        self.populate_db()

    def populate_db(self):
        for enabled_token in FAUCET_ENABLED_TOKENS:
            token = Token()
            token.address = enabled_token['address']
            token.name = enabled_token['name']
            token.chain_id = enabled_token['chainId']
            token.max_amount_day = enabled_token['maximumAmount']
            token.type = enabled_token['type']
            token.save()

    def setUp(self):
        '''
        Set up to do before running each test
        '''
        self.native_tx_counter = 0
        self.erc20_tx_counter = 0
        self._mock(TEMP_ENV_VARS)

        self.app = create_app()
        self.app_ctx = self.app.test_request_context()
        self.app_ctx.push()

        self.client = self.app.test_client()

        with self.app_ctx:
            self._reset_db()

    def tearDown(self):
        '''
        Cleanup to do after running each test
        '''
        for p in self.patchers:
            p.stop()

        self.app_ctx.pop()
        self.app_ctx = None


class RateLimitIPBaseTest(BaseTest):
    def setUp(self):
        self.native_tx_counter = 0
        self.erc20_tx_counter = 0
        env_vars = TEMP_ENV_VARS.copy()
        env_vars['FAUCET_RATE_LIMIT_STRATEGY'] = Strategy.ip.value
        self._mock(env_vars)

        self.app = create_app()
        self.app_ctx = self.app.test_request_context()
        self.app_ctx.push()

        self.client = self.app.test_client()

        with self.app_ctx:
            self._reset_db()


class RateLimitIPorAddressBaseTest(BaseTest):
    def setUp(self):
        self.native_tx_counter = 0
        self.erc20_tx_counter = 0
        # Set rate limit strategy to IP
        env_vars = TEMP_ENV_VARS.copy()
        env_vars['FAUCET_RATE_LIMIT_STRATEGY'] = Strategy.ip_or_address.value
        self._mock(env_vars)

        self.app = create_app()
        self.app_ctx = self.app.test_request_context()
        self.app_ctx.push()

        self.client = self.app.test_client()

        with self.app_ctx:
            self._reset_db()

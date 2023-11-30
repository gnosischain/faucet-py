from api import create_app
from api.services import RateLimitStrategy, Strategy

import pytest
from conftest import api_prefix
# from mock import patch
from temp_env_var import TEMP_ENV_VARS, NATIVE_TRANSFER_TX_HASH, TOKEN_TRANSFER_TX_HASH, ZERO_ADDRESS, CAPTCHA_TEST_RESPONSE_TOKEN, NATIVE_TOKEN_AMOUNT, NATIVE_TOKEN_ADDRESS, ERC20_TOKEN_ADDRESS


class BaseTest:
    def _mock(self, mocker):
        # Mock values
        mocker.patch('api.api.claim_native', return_value=NATIVE_TRANSFER_TX_HASH)
        mocker.patch('api.api.claim_token', return_value=TOKEN_TRANSFER_TX_HASH)
        return mocker
    
    def _create_app(self, env_vars=None):
        # Instantiate app
        app = create_app()
        if env_vars:
            # Override configs
            app.config.update(env_vars)
        return app

    @pytest.fixture
    def app(self, mocker):
        mocker = self._mock(mocker)
        app = self._create_app(TEMP_ENV_VARS)
        yield app

    @pytest.fixture
    def client(self, app):
        return app.test_client()
    

class TestAPI(BaseTest):
    def test_status_route(self, app, client):
        response = client.get(api_prefix + '/status')
        assert response.status_code == 200
        assert response.get_json().get('status') == 'ok'

    def test_ask_route_parameters(self, client):
        response = client.post(api_prefix + '/ask', json={})
        assert response.status_code == 400

        # wrong chainid should return 400
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': -1,
            'amount': NATIVE_TOKEN_AMOUNT,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': NATIVE_TOKEN_ADDRESS
        })
        assert response.status_code == 400

        # wrong amount, should return 400
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
            'amount': NATIVE_TOKEN_AMOUNT + 1,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': NATIVE_TOKEN_ADDRESS
        })
        assert response.status_code == 400

        # missing recipient, should return 400
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
            'amount': NATIVE_TOKEN_AMOUNT + 1,
            'tokenAddress': NATIVE_TOKEN_ADDRESS
        })
        assert response.status_code == 400

        # wrong recipient recipient, should return 400
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
            'amount': NATIVE_TOKEN_AMOUNT + 1,
            'recipient': 'not an address',
            'tokenAddress': NATIVE_TOKEN_ADDRESS
        })
        assert response.status_code == 400

        # missing token address, should return 400
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
            'amount': NATIVE_TOKEN_AMOUNT + 1,
            'recipient': ZERO_ADDRESS
        })
        assert response.status_code == 400

        # wrong token address, should return 400
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
            'amount': NATIVE_TOKEN_AMOUNT + 1,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': 'non existing token address'
        })
        assert response.status_code == 400

    def test_ask_route_native_transaction(self, client):
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
            'amount': NATIVE_TOKEN_AMOUNT,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': NATIVE_TOKEN_ADDRESS
        })
        assert response.status_code == 200
        assert response.get_json().get('transactionHash') == NATIVE_TRANSFER_TX_HASH

    def test_ask_route_token_transaction(self, client):
        # not supported token, should return 400
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
            'amount': NATIVE_TOKEN_AMOUNT,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': '0x' + '1'*40
        })
        assert response.status_code == 400

        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
            'amount': NATIVE_TOKEN_AMOUNT,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })
        assert response.status_code == 200
        assert response.get_json().get('transactionHash') == TOKEN_TRANSFER_TX_HASH


class TestAPIWithIPLimitStrategy(BaseTest):
    @pytest.fixture
    def app(self, mocker):
        mocker = self._mock(mocker)

        # Set rate limit strategy to IP
        rate_limit_strategy = RateLimitStrategy()
        rate_limit_strategy.strategy = Strategy.ip.value

        env_vars = TEMP_ENV_VARS.copy()
        env_vars['FAUCET_RATE_LIMIT_STRATEGY'] = rate_limit_strategy

        app = self._create_app(env_vars)
        yield app

    def test_ask_route_limit_by_ip(self, client):
        # First request should return 200
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
            'amount': NATIVE_TOKEN_AMOUNT,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })
        assert response.status_code == 200

        # Second request should return 429
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
            'amount': NATIVE_TOKEN_AMOUNT,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })
        assert response.status_code == 429
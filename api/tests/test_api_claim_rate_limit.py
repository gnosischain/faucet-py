import pytest
from conftest import BaseTest, RateLimitBaseTest, api_prefix
# from mock import patch
from temp_env_var import (CAPTCHA_TEST_RESPONSE_TOKEN,
                          DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
                          ERC20_TOKEN_ADDRESS, FAUCET_CHAIN_ID, TEMP_ENV_VARS,
                          ZERO_ADDRESS)

from api.services import Strategy
from api.services.database import Transaction


class TestAPIWithIPLimitStrategy(BaseTest):

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

    def test_ask_route_limit_by_ip(self, client):
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })
        assert response.status_code == 200

        # Second request should return 429
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })
        assert response.status_code == 429


class TestAPIWithIPorRecipientLimitStrategy(RateLimitBaseTest):

    def test_ask_route_limit_by_ip_or_address(self, client):
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })

        assert response.status_code == 200
        # let's store the tx_hash
        tx_hash = response.get_json()['transactionHash']

        # Second request should return 429, either IP or recipient did
        # create a transaction in the last X hours
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })
        assert response.status_code == 429

        # Change IP on DB
        fake_ip = '192.168.10.155'
        transaction = Transaction.get_by_hash(tx_hash)
        transaction.requester_ip = fake_ip
        transaction.save()

        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })

        assert response.status_code == 429

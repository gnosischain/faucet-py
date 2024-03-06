import pytest
from conftest import BaseTest, api_prefix
from flask_migrate import upgrade
# from mock import patch
from temp_env_var import (CAPTCHA_TEST_RESPONSE_TOKEN,
                          DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
                          DEFAULT_NATIVE_MAX_AMOUNT_PER_DAY,
                          ERC20_TOKEN_ADDRESS, FAUCET_CHAIN_ID,
                          NATIVE_TOKEN_ADDRESS, NATIVE_TRANSFER_TX_HASH,
                          TEMP_ENV_VARS, TOKEN_TRANSFER_TX_HASH, ZERO_ADDRESS)

from api.services import Strategy
from api.services.database import AccessKey, Transaction
from api.utils import generate_access_key


class TestAPI(BaseTest):

    def test_status_route(self, client):
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
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': NATIVE_TOKEN_ADDRESS
        })
        assert response.status_code == 400

        # wrong amount, should return 400
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY + 1,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': NATIVE_TOKEN_ADDRESS
        })
        assert response.status_code == 400

        # missing recipient, should return 400
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY + 1,
            'tokenAddress': NATIVE_TOKEN_ADDRESS
        })
        assert response.status_code == 400

        # wrong recipient recipient, should return 400
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY + 1,
            'recipient': 'not an address',
            'tokenAddress': NATIVE_TOKEN_ADDRESS
        })
        assert response.status_code == 400

        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': '0x00000123',
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })
        assert response.status_code == 400

        # missing token address, should return 400
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY + 1,
            'recipient': ZERO_ADDRESS
        })
        assert response.status_code == 400

        # wrong token address, should return 400
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY + 1,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': 'non existing token address'
        })
        assert response.status_code == 400

    def test_ask_route_native_transaction(self, client):
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_NATIVE_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': NATIVE_TOKEN_ADDRESS
        })
        assert response.status_code == 200
        assert response.get_json().get('transactionHash') == NATIVE_TRANSFER_TX_HASH

    def test_ask_route_token_transaction(self, client):
        # not supported token, should return 400
        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': '0x' + '1' * 40
        })
        assert response.status_code == 400

        response = client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })
        assert response.status_code == 200
        assert response.get_json().get('transactionHash') == TOKEN_TRANSFER_TX_HASH

        transaction = Transaction.query.with_entities(Transaction.hash).filter_by(hash=TOKEN_TRANSFER_TX_HASH).first()
        assert len(transaction) == 1
        assert transaction[0] == TOKEN_TRANSFER_TX_HASH


class TestCliAPI(BaseTest):
    def test_ask_route_parameters(self, client):
        access_key_id, secret_access_key = generate_access_key()
        http_headers = {
            'X-faucet-access-key-id': access_key_id,
            'X-faucet-secret-access-key': secret_access_key
        }

        response = client.post(api_prefix + '/cli/ask', json={})
        # Missing headers
        assert response.status_code == 400

        response = client.post(api_prefix + '/cli/ask', headers=http_headers, json={
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })
        # Access denied, not existing keys
        assert response.status_code == 403

        # Create keys on DB
        AccessKey(access_key_id=access_key_id, secret_access_key=secret_access_key).save()

        response = client.post(api_prefix + '/cli/ask', headers=http_headers, json={
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })
        assert response.status_code == 200


class TestAPIWithIPLimitStrategy(BaseTest):

    @pytest.fixture
    def app(self, mocker):
        # Set rate limit strategy to IP
        env_vars = TEMP_ENV_VARS.copy()
        env_vars['FAUCET_RATE_LIMIT_STRATEGY'] = Strategy.ip.value

        mocker = self._mock(mocker, env_vars)

        app = self._create_app()
        with app.app_context():
            upgrade()
            self.populate_db()
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

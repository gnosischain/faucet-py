from conftest import BaseTest, api_prefix
# from mock import patch
from temp_env_var import (CAPTCHA_TEST_RESPONSE_TOKEN,
                          DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
                          DEFAULT_NATIVE_MAX_AMOUNT_PER_DAY,
                          ERC20_TOKEN_ADDRESS, FAUCET_CHAIN_ID,
                          NATIVE_TOKEN_ADDRESS, NATIVE_TRANSFER_TX_HASH,
                          TOKEN_TRANSFER_TX_HASH, ZERO_ADDRESS)

from api.services.database import Transaction


class TestAPI(BaseTest):

    def test_status_route(self, client):
        response = client.get(api_prefix + '/status')
        assert response.status_code == 200
        assert response.get_json().get('status') == 'ok'

    def test_info_route(self, client):
        response = client.get(api_prefix + '/info')
        assert response.status_code == 200

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

    def test_ask_route_token_transaction(self, client, *args, **kwargs):
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

        transaction = Transaction.get_by_hash(TOKEN_TRANSFER_TX_HASH)
        assert transaction.hash == TOKEN_TRANSFER_TX_HASH

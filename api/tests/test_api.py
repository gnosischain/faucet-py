import unittest

from api.const import ZERO_ADDRESS
from api.services import CSRF
from api.services.database import BlockedUsers, Transaction

from .conftest import BaseTest, api_prefix
# from mock import patch
from .temp_env_var import (CAPTCHA_TEST_RESPONSE_TOKEN,
                           DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
                           DEFAULT_NATIVE_MAX_AMOUNT_PER_DAY,
                           ERC20_TOKEN_ADDRESS, FAUCET_CHAIN_ID,
                           NATIVE_TOKEN_ADDRESS)


class TestAPI(BaseTest):

    def test_status_route(self):
        response = self.client.get(api_prefix + '/status')
        self.assertEqual(response.status_code, 200)
        assert response.get_json().get('status') == 'ok'

    def test_info_route(self):
        response = self.client.get(api_prefix + '/info')
        self.assertEqual(response.status_code, 200)

    def test_ask_route_parameters(self):
        response = self.client.post(api_prefix + '/ask', json={})
        self.assertEqual(response.status_code, 400)

        # wrong chainid should return 400
        response = self.client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': -1,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': NATIVE_TOKEN_ADDRESS,
            'requestId': self.csrf_token.request_id,
            'timestamp': self.csrf_token.timestamp
        }, headers={
            'X-CSRFToken': self.csrf_token.token
        })
        self.assertEqual(response.status_code, 400)

        # wrong amount, should return 400
        response = self.client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY + 1,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': NATIVE_TOKEN_ADDRESS,
            'requestId': self.csrf_token.request_id,
            'timestamp': self.csrf_token.timestamp
        }, headers={
            'X-CSRFToken': self.csrf_token.token
        })
        self.assertEqual(response.status_code, 400)

        # missing recipient, should return 400
        response = self.client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY + 1,
            'tokenAddress': NATIVE_TOKEN_ADDRESS,
            'requestId': self.csrf_token.request_id,
            'timestamp': self.csrf_token.timestamp
        }, headers={
            'X-CSRFToken': self.csrf_token.token
        })
        self.assertEqual(response.status_code, 400)

        # wrong recipient recipient, should return 400
        response = self.client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY + 1,
            'recipient': 'not an address',
            'tokenAddress': NATIVE_TOKEN_ADDRESS,
            'requestId': self.csrf_token.request_id,
            'timestamp': self.csrf_token.timestamp
        }, headers={
            'X-CSRFToken': self.csrf_token.token
        })
        self.assertEqual(response.status_code, 400)

        response = self.client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': '0x00000123',
            'tokenAddress': ERC20_TOKEN_ADDRESS,
            'requestId': self.csrf_token.request_id,
            'timestamp': self.csrf_token.timestamp
        }, headers={
            'X-CSRFToken': self.csrf_token.token
        })
        self.assertEqual(response.status_code, 400)

        # missing token address, should return 400
        response = self.client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY + 1,
            'recipient': ZERO_ADDRESS,
            'requestId': self.csrf_token.request_id,
            'timestamp': self.csrf_token.timestamp
        }, headers={
            'X-CSRFToken': self.csrf_token.token
        })
        self.assertEqual(response.status_code, 400)

        # wrong token address, should return 400
        response = self.client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY + 1,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': 'non existing token address',
            'requestId': self.csrf_token.request_id,
            'timestamp': self.csrf_token.timestamp
        }, headers={
            'X-CSRFToken': self.csrf_token.token
        })
        self.assertEqual(response.status_code, 400)

    def test_ask_route_native_transaction(self):
        response = self.client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_NATIVE_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': NATIVE_TOKEN_ADDRESS,
            'requestId': self.csrf_token.request_id,
            'timestamp': self.csrf_token.timestamp
        }, headers={
            'X-CSRFToken': self.csrf_token.token
        })
        transaction = Transaction.query.filter_by(recipient=ZERO_ADDRESS).first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json().get('transactionHash'),
                         transaction.hash)

    def test_ask_route_token_transaction(self):
        # not supported token, should return 400
        response = self.client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': '0x' + '1234' * 10,
            'requestId': self.csrf_token.request_id,
            'timestamp': self.csrf_token.timestamp
        }, headers={
            'X-CSRFToken': self.csrf_token.token
        })
        self.assertEqual(response.status_code, 400)

        response = self.client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS,
            'requestId': self.csrf_token.request_id,
            'timestamp': self.csrf_token.timestamp
        }, headers={
            'X-CSRFToken': self.csrf_token.token
        })
        transaction = Transaction.query.filter_by(recipient=ZERO_ADDRESS).first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json().get('transactionHash'),
                         transaction.hash)

    def test_ask_route_blocked_users(self):
        response = self.client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS,
            'requestId': self.csrf_token.request_id,
            'timestamp': self.csrf_token.timestamp
        }, headers={
            'X-CSRFToken': self.csrf_token.token
        })
        self.assertEqual(response.status_code, 200)

        # Add recipient to BlockedUsers
        blocked_user = BlockedUsers(address=ZERO_ADDRESS)
        blocked_user.save()

        response = self.client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS,
            'requestId': self.csrf_token.request_id,
            'timestamp': self.csrf_token.timestamp
        }, headers={
            'X-CSRFToken': self.csrf_token.token
        })
        self.assertEqual(response.status_code, 403)


if __name__ == '__main__':
    unittest.main()

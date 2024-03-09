import unittest

from api.const import ZERO_ADDRESS
from api.services.database import Transaction

from .conftest import (RateLimitIPBaseTest, RateLimitIPorAddressBaseTest,
                       api_prefix)
# from mock import patch
from .temp_env_var import (CAPTCHA_TEST_RESPONSE_TOKEN,
                           DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
                           ERC20_TOKEN_ADDRESS, FAUCET_CHAIN_ID)


class TestAPIWithIPLimitStrategy(RateLimitIPBaseTest):

    def test_ask_route_limit_by_ip(self):
        response = self.client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })
        self.assertEqual(response.status_code, 200)

        # Second request should return 429
        response = self.client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })
        self.assertEqual(response.status_code, 429)


class TestAPIWithIPorRecipientLimitStrategy(RateLimitIPorAddressBaseTest):

    def test_ask_route_limit_by_ip_or_address(self):
        response = self.client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })

        self.assertEqual(response.status_code, 200)
        # let's store the tx_hash
        tx_hash = response.get_json()['transactionHash']

        # Second request should return 429, either IP or recipient did
        # create a transaction in the last X hours
        response = self.client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })
        self.assertEqual(response.status_code, 429)

        # Change IP on DB
        fake_ip = '192.168.10.155'
        transaction = Transaction.get_by_hash(tx_hash)
        transaction.requester_ip = fake_ip
        transaction.save()

        response = self.client.post(api_prefix + '/ask', json={
            'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })
        self.assertEqual(response.status_code, 429)


if __name__ == '__main__':
    unittest.main()

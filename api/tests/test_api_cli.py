from conftest import BaseTest, api_prefix
# from mock import patch
from temp_env_var import (DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
                          ERC20_TOKEN_ADDRESS, FAUCET_CHAIN_ID)

from api.const import ZERO_ADDRESS
from api.services.database import AccessKey, AccessKeyConfig
from api.utils import generate_access_key


class TestAPICli(BaseTest):
    def test_ask_route_parameters(self):
        access_key_id, secret_access_key = generate_access_key()
        http_headers = {
            'X-faucet-access-key-id': access_key_id,
            'X-faucet-secret-access-key': secret_access_key
        }

        response = self.client.post(api_prefix + '/cli/ask', json={})
        # Missing headers
        self.assertEqual(response.status_code, 400)

        response = self.client.post(api_prefix + '/cli/ask', headers=http_headers, json={
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })
        # Access denied, not existing keys
        self.assertEqual(response.status_code, 403)

        # Create access keys on DB
        access_key = AccessKey()
        access_key.access_key_id = access_key_id
        access_key.secret_access_key = secret_access_key
        access_key.save()

        config = AccessKeyConfig()
        config.access_key_id = access_key.access_key_id
        config.chain_id = 10200
        config.erc20_max_amount_day = 10
        config.native_max_amount_day = 20
        config.save()

        response = self.client.post(api_prefix + '/cli/ask', headers=http_headers, json={
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.post(api_prefix + '/cli/ask', headers=http_headers, json={
            'chainId': FAUCET_CHAIN_ID,
            'amount': 30,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        })
        self.assertEqual(response.status_code, 429)

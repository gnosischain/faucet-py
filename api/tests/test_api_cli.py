from conftest import BaseTest, api_prefix
# from mock import patch
from temp_env_var import (DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
                          ERC20_TOKEN_ADDRESS, FAUCET_CHAIN_ID,
                          ZERO_ADDRESS)

from api.services.database import AccessKey
from api.utils import generate_access_key


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

from typing import Any
import unittest
import datetime

from api.services.validator import AskEndpointValidator
from .conftest import ClaimValidationEnabledBaseTest
from .temp_env_var import (TEMP_ENV_VARS, FAUCET_CHAIN_ID,
                           DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
                           ERC20_TOKEN_ADDRESS)


ZERO_ADDRESS = '0x' + '0' * 40
claim_post_id = 0
claim_thread_id = 0
claim_api_url = "%s/t/%d/posts.json" % (TEMP_ENV_VARS['CLAIM_VALIDATION_DISCOURSE_API_URL'],
                                        claim_thread_id)

# http://myforum.gnosis.io/t/0/0
def mock_requests_request():
    # Mock object:
    # URL => response
    dt_now = datetime.datetime.now(datetime.timezone.utc)  # .strftime("%m/%d/%YT%H:%M:%S.%f")


    claim_validation_response = {
        claim_api_url: {
            'post_stream': {
                'posts': [
                    {
                        'created_at': dt_now.isoformat(),  # e.g. 2024-04-26T09:35:14.854Z
                        'cooked': '<p>%s</p>' % ZERO_ADDRESS
                    }
                ]
            }
        }
    }

    class Response:
        def __init__(self, data):
            self._data = data
            self.ok = True

        def json(self):
            return self._data

    class Request:
        def get(self, key):
            data = claim_validation_response.get(key,
                                                 'unhandled request %s' % key)
            return Response(data)
    return Request()


def mock_flask_request():
    class Environ:
        @classmethod
        def get(self, *args):
            return '127.0.0.0'

    class Request:
        remote_addr = '127.0.0.0'

        def __getattribute__(self, name: str) -> Any:
            if name == 'environ':
                return Environ
    return Request()


class TestClaimValidationEnabled(ClaimValidationEnabledBaseTest):
    @unittest.mock.patch('api.services.validator.requests',
                         mock_requests_request())
    @unittest.mock.patch('api.services.validator.request',
                         mock_flask_request())
    def test_claim_url_validation(self, *args):
        claim_validation_url = '%s/t/faucet-requests-test/%d/%d' % (TEMP_ENV_VARS['CLAIM_VALIDATION_ALLOWED_WEBSITE'],
                                               claim_post_id,
                                               claim_thread_id)
        request_data = {
            'claimValidationURL': claim_validation_url,
            'chainId': FAUCET_CHAIN_ID,
            'amount': DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
            'recipient': ZERO_ADDRESS,
            'tokenAddress': ERC20_TOKEN_ADDRESS
        }
        request_headers = {}
        validate_captcha = False
        validate_csrf = False
        validate_claim_url = True
        validator = AskEndpointValidator(request_data,
                                         request_headers,
                                         validate_captcha,
                                         validate_csrf,
                                         validate_claim_url)

        self.assertTrue(len(validator.errors) == 0)
        self.assertTrue(validator.validate())

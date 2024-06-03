from .conftest import BaseTest

from datetime import datetime


class TestCSRF(BaseTest):

    def test_values(self):
        timestamp = datetime(2020, 1, 18, 9, 30, 0).timestamp()
        token_obj = self.csrf.generate_token(timestamp=timestamp)
        self.assertTrue(
            self.csrf.validate_token(token_obj.request_id, token_obj.token, token_obj.timestamp)
        )
        self.assertFalse(
            self.csrf.validate_token('myfakeid', token_obj.token, token_obj.timestamp)
        )
        self.assertFalse(
            self.csrf.validate_token('myfakeid', 'myfaketoken', token_obj.timestamp)
        )
        self.assertFalse(
            self.csrf.validate_token(token_obj.request_id, 'myfaketoken', token_obj.timestamp)
        )
        # test with timestamp for which diff between now() and creation time in seconds
        # is lower than min. waiting period.
        # Validation must return False since time interval is lower than mimimum waiting period.
        timestamp = datetime.now().timestamp()
        token_obj = self.csrf.generate_token(timestamp=timestamp)
        self.assertFalse(
            self.csrf.validate_token(token_obj.request_id, token_obj.token, token_obj.timestamp)
        )

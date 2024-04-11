from .conftest import BaseTest


class TestCSRF(BaseTest):

    def test_values(self):
        token_obj = self.csrf.generate_token()
        self.assertTrue(
            self.csrf.validate_token(token_obj.request_id, token_obj.token)
        )
        self.assertFalse(
            self.csrf.validate_token('myfakeid', token_obj.token)
        )
        self.assertFalse(
            self.csrf.validate_token('myfakeid', 'myfaketoken')
        )
        self.assertFalse(
            self.csrf.validate_token(token_obj.request_id, 'myfaketoken')
        )

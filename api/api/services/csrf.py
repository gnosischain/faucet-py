# from api.settings import CSRF_TIMESTAMP_MAX_SECONDS

import random
from datetime import datetime

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

# Waiting period: the minimum time interval between the UI asks
# for the CSFR token to /api/v1/info and the time the UI can ask for funds.
# This check aims to block any bots that could be triggering actions through the UI.
CSRF_TIMESTAMP_MIN_SECONDS = 5


class CSRFTokenItem:
    def __init__(self, request_id, token, timestamp):
        self.request_id = request_id
        self.token = token
        self.timestamp = timestamp


class CSRFToken:
    def __init__(self, privkey, salt):
        self._privkey = RSA.import_key(privkey)
        self._pubkey = self._privkey.publickey()
        self._salt = salt

    def generate_token(self, timestamp=None):
        request_id = '%d' % random.randint(0, 1000)
        if not timestamp:
            timestamp = datetime.now().timestamp()
        data_to_encrypt = '%s%s%f' % (request_id, self._salt, timestamp)

        cipher_rsa = PKCS1_OAEP.new(self._pubkey)
        # Data_to_encrypt can be of variable length, but not longer than
        # the RSA modulus (in bytes) minus 2, minus twice the hash output size.
        # For instance, if you use RSA 2048 and SHA-256, the longest
        # message you can encrypt is 190 byte long.
        token = cipher_rsa.encrypt(data_to_encrypt.encode())

        return CSRFTokenItem(request_id, token.hex(), timestamp)

    def validate_token(self, request_id, token, timestamp):
        try:
            cipher_rsa = PKCS1_OAEP.new(self._privkey)
            decrypted_text = cipher_rsa.decrypt(bytes.fromhex(token)).decode()
            expected_text = '%s%s%f' % (request_id, self._salt, timestamp)
            if decrypted_text == expected_text:
                # Check that the timestamp is OK, the diff between now() and creation time in seconds
                # must be greater than the minimum waiting period.
                # Waiting period: the minimum time interval between UI asks for the CSFR token and the time the UI can ask for funds.
                seconds_diff = (datetime.now()-datetime.fromtimestamp(timestamp)).total_seconds()
                if seconds_diff > CSRF_TIMESTAMP_MIN_SECONDS:
                    return True
                return False
            return False
        except Exception:
            return False


class CSRF:
    _instance = None

    def __new__(cls, privatekey, salt):
        if not hasattr(cls, 'instance'):
            cls.instance = CSRFToken(privatekey, salt)
        return cls.instance

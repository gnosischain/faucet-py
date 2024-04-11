
import random

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


class CSRFTokenItem:
    def __init__(self, request_id, token):
        self.request_id = request_id
        self.token = token


class CSRFToken:
    def __init__(self, privkey, salt):
        self._privkey = RSA.import_key(privkey)
        self._pubkey = self._privkey.publickey()
        self._salt = salt

    def generate_token(self):
        request_id = '%d' % random.randint(0, 1000)
        data_to_encrypt = '%s%s' % (request_id, self._salt)

        cipher_rsa = PKCS1_OAEP.new(self._pubkey)
        token = cipher_rsa.encrypt(data_to_encrypt.encode())

        return CSRFTokenItem(request_id, token.hex())

    def validate_token(self, request_id, token):
        cipher_rsa = PKCS1_OAEP.new(self._privkey)
        decrypted_text = cipher_rsa.decrypt(bytes.fromhex(token)).decode()

        expected_text = '%s%s' % (request_id, self._salt)
        if decrypted_text == expected_text:
            return True
        return False


class CSRF:
    _instance = None

    def __new__(cls, privatekey, salt):
        if not hasattr(cls, 'instance'):
            cls.instance = CSRFToken(privatekey, salt)
        return cls.instance

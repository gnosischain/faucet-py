import logging

import requests

logging.basicConfig(level=logging.INFO)


class Captcha:
    def __init__(self, provider):
        self.provider = provider

    def verify(self, client_response, catpcha_api_url, secret_key, remote_ip, site_key=None):
        logging.info('Captcha: Remote IP %s' % remote_ip)

        if self.provider == 'HCAPTCHA':
            request = requests.post(catpcha_api_url, data={
                'response': client_response,
                'secret': secret_key,
                'remoteip': remote_ip,
                'sitekey': site_key
            })

            logging.info('Captcha: verify response %s' % request.json())

            if request.status_code != 200:
                return False
            return request.json()['success'] is True
        elif self.provider == 'CLOUDFLARE':
            request = requests.post(catpcha_api_url, data={
                'response': client_response,
                'secret': secret_key,
                'remoteip': remote_ip
            })

            logging.info('Captcha: verify response %s' % request.json())

            if request.status_code != 200:
                return False
            return request.json()['success'] is True
        else:
            raise NotImplementedError


class CaptchaSingleton:
    _instance = None

    def __new__(cls, provider):
        if not hasattr(cls, 'instance'):
            cls.instance = Captcha(provider)
        return cls.instance


# def captcha_verify(client_response, catpcha_api_url, secret_key, remote_ip, site_key):
#     logging.info('Captcha: Remote IP %s' % remote_ip)
#     request = requests.post(catpcha_api_url, data={
#         'response': client_response,
#         'secret': secret_key,
#         'remoteip': remote_ip,
#         'sitekey': site_key
#     })

#     logging.info('Captcha: verify response %s' % request.json())

#     if request.status_code != 200:
#         return False
#     return request.json()['success'] == True

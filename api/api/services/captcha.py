import requests
import logging


logging.basicConfig(level=logging.INFO)


def captcha_verify(client_response, catpcha_api_url, secret_key, remote_ip, site_key):
    request = requests.post(catpcha_api_url, data={
        'response': client_response,
        'secret': secret_key,
        'remoteip': remote_ip,
        'sitekey': site_key
    })

    logging.info('Captcha verify response: %s' % request.json())

    if request.status_code != 200:
        return False
    return request.json()['success'] == True

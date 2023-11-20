import requests


def captcha_verify(client_response, catpcha_api_url, secret_key):
    request = requests.post(catpcha_api_url, data={
        'response': client_response,
        'secret': secret_key
    })

    if request.status_code != 200:
        return False
    return request.json()['success'] == True
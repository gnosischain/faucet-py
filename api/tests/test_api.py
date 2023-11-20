from conftest import api_prefix
# from mock import patch
from temp_env_var import TEMP_ENV_VARS, NATIVE_TRANSFER_TX_HASH, TOKEN_TRANSFER_TX_HASH, ZERO_ADDRESS, CAPTCHA_TEST_RESPONSE_TOKEN


def test_status_route(app, client):
    response = client.get(api_prefix + '/status')
    assert response.status_code == 200
    assert response.get_json().get('status') == 'ok'

def test_ask_route_parameters(client):
    response = client.post(api_prefix + '/ask', json={})
    assert response.status_code == 400

    # wrong chainid should return 400
    response = client.post(api_prefix + '/ask', json={
        'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
        'chainId': -1,
        'amount': TEMP_ENV_VARS['FAUCET_AMOUNT'],
        'recipient': ZERO_ADDRESS,
        'tokenAddress': 'native'
    })
    assert response.status_code == 400

    # wrong amount, should return 400
    response = client.post(api_prefix + '/ask', json={
        'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
        'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
        'amount': TEMP_ENV_VARS['FAUCET_AMOUNT'] + 1,
        'recipient': ZERO_ADDRESS,
        'tokenAddress': 'native'
    })
    assert response.status_code == 400

    # missing recipient, should return 400
    response = client.post(api_prefix + '/ask', json={
        'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
        'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
        'amount': TEMP_ENV_VARS['FAUCET_AMOUNT'] + 1,
        'tokenAddress': 'native'
    })
    assert response.status_code == 400

    # wrong recipient recipient, should return 400
    response = client.post(api_prefix + '/ask', json={
        'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
        'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
        'amount': TEMP_ENV_VARS['FAUCET_AMOUNT'] + 1,
        'recipient': 'not an address',
        'tokenAddress': 'native'
    })
    assert response.status_code == 400

    # missing token address, should return 400
    response = client.post(api_prefix + '/ask', json={
        'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
        'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
        'amount': TEMP_ENV_VARS['FAUCET_AMOUNT'] + 1,
        'recipient': ZERO_ADDRESS
    })
    assert response.status_code == 400

    # wrong token address, should return 400
    response = client.post(api_prefix + '/ask', json={
        'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
        'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
        'amount': TEMP_ENV_VARS['FAUCET_AMOUNT'] + 1,
        'recipient': ZERO_ADDRESS,
        'tokenAddress': 'non existing token address'
    })
    assert response.status_code == 400

def test_ask_route_native_transaction(client):
    response = client.post(api_prefix + '/ask', json={
        'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
        'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
        'amount': TEMP_ENV_VARS['FAUCET_AMOUNT'],
        'recipient': ZERO_ADDRESS,
        'tokenAddress': 'native'
    })
    assert response.status_code == 200
    assert response.get_json().get('transactionHash') == NATIVE_TRANSFER_TX_HASH

def test_ask_route_token_transaction(client):
    # not supported token, should return 400
    response = client.post(api_prefix + '/ask', json={
        'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
        'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
        'amount': TEMP_ENV_VARS['FAUCET_AMOUNT'],
        'recipient': ZERO_ADDRESS,
        'tokenAddress': '0x' + '1'*40
    })
    assert response.status_code == 400

    response = client.post(api_prefix + '/ask', json={
        'captcha': CAPTCHA_TEST_RESPONSE_TOKEN,
        'chainId': TEMP_ENV_VARS['FAUCET_CHAIN_ID'],
        'amount': TEMP_ENV_VARS['FAUCET_AMOUNT'],
        'recipient': ZERO_ADDRESS,
        'tokenAddress': TEMP_ENV_VARS['FAUCET_ENABLED_TOKENS'][0]['address']
    })
    assert response.status_code == 200
    assert response.get_json().get('transactionHash') == TOKEN_TRANSFER_TX_HASH
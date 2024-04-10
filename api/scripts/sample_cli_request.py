import requests

ASK_API_ENDPOINT = 'https://api.faucet.dev.gnosisdev.com/api/v1/cli/ask'
ACCESS_KEY_ID = '__ACCESS_KEY_ID__'
ACCESS_KEY_SECRET = '__ACCESS_KEY_SECRET__'

headers = {
    'X-faucet-access-key-id': ACCESS_KEY_ID,
    'X-faucet-secret-access-key': ACCESS_KEY_SECRET,
    'content-type': 'application/json'
}

json_data = {
    'tokenAddress': '0x0000000000000000000000000000000000000000',  # stands for Native token
    'amount': 0.01,
    'chainId': 10200,
    'recipient': '0xf8d0b3c2578aee1fceb9830eb92b5da007d71ba9'
}

response = requests.post(ASK_API_ENDPOINT,
                         headers=headers,
                         json=json_data)

print(response.json())

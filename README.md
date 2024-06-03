# Faucet-Py

A simple python implementation of an EVM compatible faucet.

## Python API

### Requirements

Python +3.x

### Installation

```
cd api
python3 -m venv .venv
. .venv/bin/activate
pip3 install -r requirements-dev.txt
```

### Run application

Check .env.example for reference.

```
cd api
python3 -m flask --app api run --port 8000
```

### Run tests

```
cd api
python3 -m unittest discover -p 'test_*.py'
```

Run specific test case:

```
cd api
python3 -m unittest tests.test_api.TestAPI.test_ask_route_blocked_users
```

### Run Flake8 and isort

```
cd api
python3 install -r requiremenets-dev.txt
isort **/*.py --atomic
python3 -m flake8
```

### Operations

#### Add enabled tokens

To enable tokens on the API just run the command `create_enabled_token`.
Accepted parameters: token name, chain ID, token address, maximum amount per day per user, whether native or erc20

Samples below:

```
cd /api
flask -A api create_enabled_token GNO 10200 0x19C653Da7c37c66208fbfbE8908A5051B57b4C70 0.01 erc20
flask -A api create_enabled_token xDAI 10200 0x0000000000000000000000000000000000000000 0.01 native
```

Once enabled, the token will appear in the list of enabled tokens on the endpoint `api/v1/info`.

#### Change maximum daily amounts per user

If you want to change the amount you are giving out for a specific token, make sure you have sqlite
installed on the server, e.g. apk update && apk add sqlite.

Enter the database: `sqlite path/to/database`

Search for the token to update: `select chain_id, max_amount_day from tokens where name = 'xDAI'`
Update amount: `update tokens set max_amount_day = 0.00015 where chain_id = 100;`

## ReactJS Frontend

### Requirements

NodeJS v18.x

### Installation

```
nvm use

cd app
yarn
```

### Run application

```
cd app
yarn start
```
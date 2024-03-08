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
python3 -m pytest -s
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

Once enabled, the token wil appear in the list of enabled tokens on the endpoint `api/v1/info`.

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
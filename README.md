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
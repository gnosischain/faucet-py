# Faucet-Py

A simple python implementation of an EVM compatible faucet.

## API

### Requirements

Python +3.x

### Installation

```
cd api
python3 -m venv .venv
. .venv/bin/activate
pip3 install -r requirements.txt

python3 -m flask --app api run --port 8000
```

### Run application

```
cd api
python3 -m flask --app api run --port 8000
```


### Run tests

```
cd api
python3 -m pytest -s
```
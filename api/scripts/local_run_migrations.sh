#!/bin/bash

set -x

# DB MIGRATIONS:
FLASK_APP=api FAUCET_ENABLED_CHAIN_IDS=100,10200 FAUCET_DATABASE_URI=sqlite:// python3 -m flask db init  # only the first time we initialize the DB
FLASK_APP=api FAUCET_ENABLED_CHAIN_IDS=100,10200 FAUCET_DATABASE_URI=sqlite:// python3 -m flask db migrate
# Reflect migrations into the database:
# FLASK_APP=api python3 -m flask db upgrade

# Valid SQLite URL forms are:
#  sqlite:// (in-memory)
#  sqlite:///relative/path/to/file.db
#  sqlite:////absolute/path/to/file.db
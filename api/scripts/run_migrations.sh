#!/bin/bash

set -x

# DB MIGRATIONS:
FLASK_APP=api FAUCET_DATABASE_URI=sqlite:///:memory python3 -m flask db init  # only the first time we initialize the DB
FLASK_APP=api FAUCET_DATABASE_URI=sqlite:///:memory python3 -m flask db migrate
# Reflect migrations onto the database:
# FLASK_APP=api python3 -m flask db upgrade

# Valid SQLite URL forms are:
#  sqlite:///:memory: (or, sqlite://)
#  sqlite:///relative/path/to/file.db
#  sqlite:////absolute/path/to/file.db
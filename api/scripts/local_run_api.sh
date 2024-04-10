#!/bin/bash

set -euo pipefail


echo "==> $(date +%H:%M:%S) ==> Migrating DB models... "
FLASK_APP=api python -m flask db upgrade

echo "==> $(date +%H:%M:%S) ==> Running Gunicorn... "
exec gunicorn --bind localhost:8000 "api:create_app()"
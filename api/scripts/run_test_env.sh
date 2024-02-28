touch /tmp/faucet_test.db

# !! PRIVATE KEY FOR TEST PURPOSE ONLY !!
# 0x21b1ae205147d4e2fcdee7b3fc762aa21f955f3dace8a185306ac104be797081
# !! DO NOT USE IN ANY OTHER CONTEXTS !!

FAUCET_RPC_URL=https://rpc.chiadochain.net \
FAUCET_PRIVATE_KEY="0x21b1ae205147d4e2fcdee7b3fc762aa21f955f3dace8a185306ac104be797081" \
FAUCET_CHAIN_ID=10200 \
FAUCET_DATABASE_URI=sqlite:///tmp/faucet_test.db \
CAPTCHA_VERIFY_ENDPOINT=localhost \
CAPTCHA_SECRET_KEY=testkey \
python3 -m flask --app api run --port 8000

#   DB MIGRATIONS:
##   Generate migrations
###  ENV_VARIABLES python3 -m flask --app api db init
###  ENV_VARIABLES python3 -m flask --app api db migrate

# Valid SQLite URL forms are:
#  sqlite:///:memory: (or, sqlite://)
#  sqlite:///relative/path/to/file.db
#  sqlite:////absolute/path/to/file.db
FLASK_APP=api FAUCET_DATABASE_URI=sqlite:///test.db python3 -m flask db upgrade
FLASK_APP=api FAUCET_DATABASE_URI=sqlite:///test.db python3 -m flask create_enabled_token xDAI 10200 0x0000000000000000000000000000000000000000 10 native
FLASK_APP=api FAUCET_DATABASE_URI=sqlite:///test.db python3 -m flask create_access_keys
# Take note of the access keys
# Run API on port 3000
FLASK_APP=api FAUCET_DATABASE_URI=sqlite:///test.db python3 -m flask run -p 3000
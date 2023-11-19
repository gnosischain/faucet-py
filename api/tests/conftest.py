import pytest
from api import create_app
from temp_env_var import TEMP_ENV_VARS, NATIVE_TRANSFER_TX_HASH, TOKEN_TRANSFER_TX_HASH

api_prefix = '/api/v1'


@pytest.fixture
def app(mocker):
    # Mock values
    mocker.patch('api.api.claim_native', return_value=NATIVE_TRANSFER_TX_HASH)
    mocker.patch('api.api.claim_token', return_value=TOKEN_TRANSFER_TX_HASH)
    # Instantiate app
    app = create_app()
    # Override configs
    app.config.update(TEMP_ENV_VARS)

    yield app

@pytest.fixture
def client(app):
    return app.test_client()
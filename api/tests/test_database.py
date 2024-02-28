from conftest import BaseTest

from api.services.database import AccessKey
from api.utils import generate_access_key


class TestDatabase(BaseTest):

    # db.create_all()  # Create database tables for our data models

    def test_models(self, client):
        access_key_id, secret_access_key = generate_access_key()
        assert len(access_key_id) == 16
        assert len(secret_access_key) == 32
        access_key = AccessKey()
        access_key.access_key_id = access_key_id
        access_key.secret_access_key = secret_access_key
        access_key.save()
        result = AccessKey.query.filter_by(access_key_id=access_key_id, secret_access_key=secret_access_key).all()
        assert len(result) == 1  # we just have 1 item for that key ID and access key
        assert result[0].access_key_id == access_key_id
        assert result[0].secret_access_key == secret_access_key
        assert result[0].enabled is True

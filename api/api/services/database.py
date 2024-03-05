import sqlite3

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


class Database:
    def __init__(self, connection_uri):
        self.connection = sqlite3.connect(connection_uri)

    def get_connection(self):
        self.connection.row_factory = sqlite3.Row
        return self.connection


class DatabaseSingleton:
    _instance = None

    def __new__(cls, connection_uri):
        if not hasattr(cls, 'instance'):
            cls.instance = Database(connection_uri)
        return cls.instance


# DATABASE models

class BaseModel(db.Model):
    __abstract__ = True

    def before_save(self, *args, **kwargs):
        pass

    def after_save(self, *args, **kwargs):
        pass

    def save(self, commit=True):
        self.before_save()
        db.session.add(self)
        if commit:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e

        self.after_save()

    def before_update(self, *args, **kwargs):
        pass

    def after_update(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        self.before_update(*args, **kwargs)
        db.session.commit()
        self.after_update(*args, **kwargs)

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()


class AccessKey(BaseModel):
    __tablename__ = "access_keys"
    access_key_id = db.Column(db.String(16), primary_key=True)
    secret_access_key = db.Column(db.String(32))
    enabled = db.Column(db.Boolean(), default=True)

    def __repr__(self):
        return f"<Access Key {self.access_key_id}>"

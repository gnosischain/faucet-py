import sqlite3

from flask_sqlalchemy import SQLAlchemy

from api.const import (DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
                       DEFAULT_FAUCET_REQUEST_TYPE,
                       DEFAULT_NATIVE_MAX_AMOUNT_PER_DAY)

db = SQLAlchemy()


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


class Token(BaseModel):
    name = db.Column(db.String(10), nullable=False)
    chain_id = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(42), primary_key=True)
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    max_amount_day = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(6), nullable=False)  # native, erc20

    __tablename__ = "tokens"


class AccessKey(BaseModel):
    access_key_id = db.Column(db.String(16), primary_key=True)
    secret_access_key = db.Column(db.String(32), nullable=False)
    enabled = db.Column(db.Boolean, default=True, nullable=False)

    __tablename__ = "access_keys"

    def __repr__(self):
        return f"<Access Key {self.access_key_id}>"


class AccessKeyConfig(BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    erc20_max_amount_day = db.Column(db.Integer, nullable=False, default=DEFAULT_ERC20_MAX_AMOUNT_PER_DAY)
    native_max_amount_day = db.Column(db.Integer, nullable=False, default=DEFAULT_NATIVE_MAX_AMOUNT_PER_DAY)
    access_key_id = db.Column(db.String, db.ForeignKey('access_keys.access_key_id'))
    chain_id = db.Column(db.Integer, nullable=False)

    __tablename__ = "access_keys_config"
    __table_args__ = tuple(
        db.PrimaryKeyConstraint('access_key_id', 'chain_id')
    )


class Transactions(BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column(db.String(32), nullable=False)
    recipient = db.Column(db.String(42), nullable=False)
    token = db.Column(db.String, db.ForeignKey('tokens.address'))
    type = db.Column(db.String(10), nullable=False, default=DEFAULT_FAUCET_REQUEST_TYPE)
    access_key_id = db.Column(db.String, db.ForeignKey('access_keys.access_key_id'), nullable=True)

    __tablename__ = "transactions"
    __table_args__ = tuple(
        db.PrimaryKeyConstraint('hash', 'token')
    )

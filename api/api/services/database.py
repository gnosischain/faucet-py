import sqlite3
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from api.const import (DEFAULT_ERC20_MAX_AMOUNT_PER_DAY,
                       DEFAULT_NATIVE_MAX_AMOUNT_PER_DAY, FaucetRequestType)

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

    @classmethod
    def enabled_tokens(cls):
        return cls.query.filter_by(enabled=True).all()

    @classmethod
    def get_by_address(cls, address):
        return cls.query.filter_by(address=address).first()
    
    @classmethod
    def get_by_address_and_chain_id(cls, address, chain_id):
        return cls.query.filter_by(address=address,
                                   chain_id=chain_id).first()


class AccessKey(BaseModel):
    access_key_id = db.Column(db.String(16), primary_key=True)
    secret_access_key = db.Column(db.String(32), nullable=False)
    enabled = db.Column(db.Boolean, default=True, nullable=False)

    __tablename__ = "access_keys"
    __table_args__ = (
        db.UniqueConstraint('secret_access_key'),
    )

    def __repr__(self):
        return f"<Access Key {self.access_key_id}>"

    @classmethod
    def get_by_key_id(cls, access_key_id):
        return cls.query.filter_by(access_key_id=access_key_id).first()


class AccessKeyConfig(BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    erc20_max_amount_day = db.Column(db.Integer, nullable=False, default=DEFAULT_ERC20_MAX_AMOUNT_PER_DAY)
    native_max_amount_day = db.Column(db.Integer, nullable=False, default=DEFAULT_NATIVE_MAX_AMOUNT_PER_DAY)
    access_key_id = db.Column(db.String, db.ForeignKey('access_keys.access_key_id'))
    chain_id = db.Column(db.Integer, nullable=False)

    __tablename__ = "access_keys_config"
    __table_args__ = (
        db.UniqueConstraint('access_key_id', 'chain_id'),
    )

    @classmethod
    def get_by_key_id_and_chain_id(cls, access_key_id, chain_id):
        return cls.query.filter_by(access_key_id=access_key_id,
                                   chain_id=chain_id).first()


class Transaction(BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column(db.String(32), nullable=False)
    recipient = db.Column(db.String(42), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    token = db.Column(db.String, db.ForeignKey('tokens.address'))
    type = db.Column(db.String(10), nullable=False, default=FaucetRequestType.web.value)
    access_key_id = db.Column(db.String, db.ForeignKey('access_keys.access_key_id'), nullable=True)
    requester_ip = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __tablename__ = "transactions"
    __table_args__ = (
        db.UniqueConstraint('hash'),
    )

    @classmethod
    def last_by_recipient(cls, recipient):
        return cls.query.filter_by(recipient=recipient).order_by(cls.created.desc()).first()

    @classmethod
    def last_by_ip(cls, ip):
        return cls.query.filter_by(requester_ip=ip).order_by(cls.created.desc()).first()

    @classmethod
    def last_by_ip_and_recipient(cls, ip, recipient):
        return cls.query.filter_by(requester_ip=ip, recipient=recipient).order_by(cls.created.desc()).first()

    @classmethod
    def last_by_ip_or_recipient(cls, ip, recipient):
        return cls.query.filter(
            ((cls.requester_ip == ip) | (cls.recipient == recipient))
        ).order_by(cls.created.desc()).first()

    @classmethod
    def get_by_hash(cls, hash):
        return cls.query.filter_by(hash=hash).first()
    
    @classmethod
    def get_amount_sum_by_access_key_and_token(cls,
                                               access_key_id,
                                               token_address,
                                               custom_timerange=None):
        if custom_timerange:
            return cls.query.with_entities(
                    db.func.sum(cls.amount).label('amount')
                ).filter_by(
                    access_key_id=access_key_id,
                    token=token_address,
                ).filter(
                    cls.created >= custom_timerange
                ).first().amount
        else:
            return cls.query.with_entities(
                    db.func.sum(cls.amount).label('amount')
                ).filter_by(
                    access_key_id=access_key_id,
                    token=token_address
                ).first().amount

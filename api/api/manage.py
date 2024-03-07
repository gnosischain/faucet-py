import logging

import click
from flask import current_app
from flask.cli import with_appcontext

from .services import Web3Singleton
from .services.database import AccessKey, AccessKeyConfig, Token
from .utils import generate_access_key


@click.command(name='create_access_keys')
@with_appcontext
def create_access_keys_cmd():
    access_key_id, secret_access_key = generate_access_key()
    access_key = AccessKey()
    access_key.access_key_id = access_key_id
    access_key.secret_access_key = secret_access_key
    access_key.save()

    config = AccessKeyConfig()
    config.access_key_id = access_key.access_key_id
    config.chain_id = current_app.config["FAUCET_CHAIN_ID"]
    config.save()

    logging.info(f'Access Key ID    : ${access_key_id}')
    logging.info(f'Secret access key: ${secret_access_key}')


@click.command(name='create_enabled_token')
@click.argument('name')
@click.argument('chain_id')
@click.argument('address')
@click.argument('max_amount_day')
@click.argument('type')
@with_appcontext
def create_enabled_token_cmd(name, chain_id, address, max_amount_day, type):
    w3 = Web3Singleton(
        current_app.config['FAUCET_RPC_URL'],
        current_app.config['FAUCET_PRIVATE_KEY']
    )

    # check if Token already exists
    check_token = Token.get_by_address(w3.to_checksum_address(address))

    if check_token:
        raise Exception('Token %s already exists' % address)

    # Checks
    if type.lower() not in ('native', 'erc20'):
        raise Exception('Type must be any of (erc20, native) got %s' % type)
    if float(max_amount_day) <= 0:
        raise Exception('Max amount per day must be greater than 0, got %d' % float(max_amount_day))

    token = Token()
    token.name = name
    token.chain_id = chain_id
    token.address = w3.to_checksum_address(address)
    token.max_amount_day = float(max_amount_day)
    token.type = type
    token.enabled = True
    token.save()

    logging.info('Token created successfully')

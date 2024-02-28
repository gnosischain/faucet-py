import logging

import click
from flask.cli import with_appcontext

from .services.database import AccessKey
from .utils import generate_access_key


@click.command(name='create_access_keys')
@with_appcontext
def create_access_keys_cmd():
    access_key_id, secret_access_key = generate_access_key()
    access_key = AccessKey()
    access_key.access_key_id = access_key_id
    access_key.secret_access_key = secret_access_key
    access_key.save()
    logging.info(f'Access Key ID    : ${access_key_id}')
    logging.info(f'Secret access key: ${secret_access_key}')

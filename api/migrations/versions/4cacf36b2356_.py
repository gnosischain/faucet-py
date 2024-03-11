"""empty message

Revision ID: 4cacf36b2356
Revises: 022497197c7a
Create Date: 2024-03-09 11:37:03.009350

"""
from alembic import op
import sqlalchemy as sa

from api.services.database import flask_db_convention


# revision identifiers, used by Alembic.
revision = '4cacf36b2356'
down_revision = '022497197c7a'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('access_keys', schema=None, naming_convention=flask_db_convention) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_access_keys_secret_access_key'), ['secret_access_key'])

    with op.batch_alter_table('access_keys_config', schema=None, naming_convention=flask_db_convention) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_access_keys_config_access_key_id'), ['access_key_id', 'chain_id'])

    with op.batch_alter_table('transactions', schema=None, naming_convention=flask_db_convention) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_transactions_hash'), ['hash'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transactions', schema=None, naming_convention=flask_db_convention) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_transactions_hash'), type_='unique')

    with op.batch_alter_table('access_keys_config', schema=None, naming_convention=flask_db_convention) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_access_keys_config_access_key_id'), type_='unique')

    with op.batch_alter_table('access_keys', schema=None, naming_convention=flask_db_convention) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_access_keys_secret_access_key'), type_='unique')

    # ### end Alembic commands ###

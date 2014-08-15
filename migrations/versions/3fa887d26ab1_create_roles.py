"""insert roles

Revision ID: 3fa887d26ab1
Revises: 1d72ca5efe15
Create Date: 2014-08-12 21:16:24.657926

"""

# revision identifiers, used by Alembic.
revision = '3fa887d26ab1'
down_revision = '1d72ca5efe15'

from alembic import op
import sqlalchemy as sa

roles_table = sa.sql.table('roles',
                           sa.sql.column('id', sa.Integer),
                           sa.sql.column('name', sa.String))


def upgrade():
    op.bulk_insert(roles_table,
                   [{'id': 1, 'name': 'admin'},
                    {'id': 2, 'name': 'user'}])


def downgrade():
    op.execute(roles_table.delete().
               where(roles_table.c.id == op.inline_literal(1)))
    op.execute(roles_table.delete().
               where(roles_table.c.id == op.inline_literal(2)))

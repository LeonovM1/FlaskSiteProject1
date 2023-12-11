"""Изменение названия столбца Description на description

Revision ID: 8c20b721a429
Revises: 7c3828446905
Create Date: 2023-12-10 02:57:05.616534

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c20b721a429'
down_revision = '7c3828446905'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('Product', 'Description', new_column_name='description',
    schema='FlaskSite'
    )

def downgrade():
    op.alter_column('Product', 'dectription', new_column_name='Description',
    schema='FlaskSite'
    )
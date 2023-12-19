"""empty message

Revision ID: 62fff43fc587
Revises: 892d7f581dce
Create Date: 2023-12-19 02:12:05.896481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62fff43fc587'
down_revision = '892d7f581dce'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('User', 'password', existing_type=sa.String(120), type_=sa.Text, schema='FlaskSite')
    

def downgrade():
        op.alter_column('User', 'password', existing_type=sa.Text, type_=sa.String(120), schema='FlaskSite')

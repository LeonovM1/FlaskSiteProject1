"""Added is_confirmed to Order

Revision ID: 892d7f581dce
Revises: 9124421f01e9
Create Date: 2023-12-16 05:37:04.271699

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '892d7f581dce'
down_revision = '9124421f01e9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('Order', sa.Column('is_confirmed', sa.Boolean(), nullable=True), schema='FlaskSite')


def downgrade():
    op.drop_column('Order', 'is_confirmed', schema='FlaskSite')

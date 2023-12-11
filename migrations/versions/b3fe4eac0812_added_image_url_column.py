"""Added image_url column

Revision ID: b3fe4eac0812
Revises: 
Create Date: 2023-12-08 02:24:26.530055

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3fe4eac0812'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('User', 'password', type_=sa.Text)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Product', 'image_url', schema='FlaskSite')
    # ### end Alembic commands ###

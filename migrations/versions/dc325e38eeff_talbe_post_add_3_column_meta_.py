"""talbe 'post' add 3 column: 'meta_description', 'meta_keywords', 'brief'

Revision ID: dc325e38eeff
Revises: 4c07d50ecfd3
Create Date: 2018-01-16 15:38:37.813344

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc325e38eeff'
down_revision = '4c07d50ecfd3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('brief', sa.String(length=512), nullable=True))
    op.add_column('post', sa.Column('meta_description', sa.String(length=128), nullable=True))
    op.add_column('post', sa.Column('meta_keywords', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'meta_keywords')
    op.drop_column('post', 'meta_description')
    op.drop_column('post', 'brief')
    # ### end Alembic commands ###
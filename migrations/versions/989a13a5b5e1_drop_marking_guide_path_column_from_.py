"""Drop marking_guide_path column from tests table

Revision ID: 989a13a5b5e1
Revises: 1bdf8e8ee88a
Create Date: 2025-08-05 02:21:35.624740

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '989a13a5b5e1'
down_revision = '1bdf8e8ee88a'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('tests') as batch_op:
        batch_op.drop_column('marking_guide_path')


def downgrade():
    with op.batch_alter_table('tests') as batch_op:
        batch_op.add_column(sa.Column('marking_guide_path', sa.String(length=255), nullable=True))

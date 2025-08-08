"""Drop marking_guide_path column from tests table

Revision ID: a9cb7ab6f15e
Revises: 989a13a5b5e1
Create Date: 2025-08-05 02:21:55.580127

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a9cb7ab6f15e'
down_revision = '989a13a5b5e1'
branch_labels = None
depends_on = None

def upgrade():
    # Drop the column 'marking_guide_path' from 'tests' table
    with op.batch_alter_table('tests') as batch_op:
        batch_op.drop_column('marking_guide_path')

def downgrade():
    # Re-add the column if downgrade is needed
    with op.batch_alter_table('tests') as batch_op:
        batch_op.add_column(sa.Column('marking_guide_path', sa.String(length=255), nullable=True))

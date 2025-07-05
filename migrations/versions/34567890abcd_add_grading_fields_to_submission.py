 """Update submission table with grading status and override fields

Revision ID: 34567890abcd
Revises: 23456789def0
Create Date: 2025-07-05 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision = '34567890abcd'
down_revision = '23456789def0'  # Adjust based on your latest migration
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('submission', sa.Column('is_graded', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('submission', sa.Column('manual_override', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('submission', sa.Column('graded_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True))
    op.add_column('submission', sa.Column('graded_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('submission', 'graded_at')
    op.drop_column('submission', 'graded_by_id')
    op.drop_column('submission', 'manual_override')
    op.drop_column('submission', 'is_graded')

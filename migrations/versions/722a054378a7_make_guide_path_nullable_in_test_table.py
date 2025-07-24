"""Make guide_path nullable in test table

Revision ID: 722a054378a7
Revises: 9ea5e3ec8f02
Create Date: 2025-07-21 19:13:39.513129

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '722a054378a7'
down_revision = '9ea5e3ec8f02'
branch_labels = None
depends_on = None


def upgrade():
    # Alter 'guide_path' to allow NULL values
    op.alter_column('test', 'guide_path',
               existing_type=sa.String(length=255),  # adjust length/type as per your model
               nullable=True)


def downgrade():
    # Revert 'guide_path' to NOT NULL
    op.alter_column('test', 'guide_path',
               existing_type=sa.String(length=255),
               nullable=False)

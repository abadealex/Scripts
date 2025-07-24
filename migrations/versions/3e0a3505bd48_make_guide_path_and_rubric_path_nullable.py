"""Make guide_path and rubric_path nullable

Revision ID: 3e0a3505bd48
Revises: 722a054378a7
Create Date: 2025-07-21 19:27:43.300833

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e0a3505bd48'
down_revision = '722a054378a7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('test', schema=None) as batch_op:
        batch_op.alter_column('guide_path',
            existing_type=sa.String(length=255),
            nullable=True)
        batch_op.alter_column('rubric_path',
            existing_type=sa.String(length=255),
            nullable=True)


def downgrade():
    with op.batch_alter_table('test', schema=None) as batch_op:
        batch_op.alter_column('guide_path',
            existing_type=sa.String(length=255),
            nullable=False)
        batch_op.alter_column('rubric_path',
            existing_type=sa.String(length=255),
            nullable=False)

    # ### end Alembic commands ###

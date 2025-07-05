"""Add AuditLog table for logging grading actions and manual overrides

Revision ID: 123456789abc
Revises: <previous_revision_id>
Create Date: 2025-07-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '123456789abc'
down_revision = '<previous_revision_id>'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(length=255), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('additional_info', sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_table('audit_logs')

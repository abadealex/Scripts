"""Add Feedback table for storing teacher feedback on answers

Revision ID: 23456789def0
Revises: 123456789abc
Create Date: 2025-07-05 12:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision = '23456789def0'
down_revision = '123456789abc'  # Should match the previous migration ID
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'feedback',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('teacher_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('student_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('answer_id', sa.Integer, sa.ForeignKey('answers.id'), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('score', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )


def downgrade():
    op.drop_table('feedback')


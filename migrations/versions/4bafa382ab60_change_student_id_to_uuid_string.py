"""Change student_id to UUID string

Revision ID: 4bafa382ab60
Revises: c637d528c20a
Create Date: 2025-07-23 01:16:03.694265
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4bafa382ab60'
down_revision = 'c637d528c20a'
branch_labels = None
depends_on = None


def upgrade():
    # Enable uuid-ossp extension (needed for uuid_generate_v5)
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Create new audit_logs table and drop old audit_log
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('submission_id', sa.Integer(), sa.ForeignKey('ocr_submission.id'), nullable=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('question_id', sa.String(length=64), nullable=False),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('original_text', sa.Text(), nullable=True),
        sa.Column('corrected_text', sa.Text(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
    )
    op.drop_table('audit_log')

    # Convert student_id columns from INTEGER to UUID using uuid_generate_v5
    for table_name in ['student_submissions', 'submission_files', 'test_submissions']:
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.alter_column(
                'student_id',
                existing_type=sa.Integer(),
                type_=postgresql.UUID(),
                postgresql_using="uuid_generate_v5(uuid_nil(), student_id::text)",
                existing_nullable=False
            )


def downgrade():
    # Revert student_id columns from UUID back to INTEGER
    for table_name in ['test_submissions', 'submission_files', 'student_submissions']:
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.alter_column(
                'student_id',
                existing_type=postgresql.UUID(),
                type_=sa.Integer(),
                existing_nullable=False
            )

    # Drop new audit_logs and recreate old audit_log table
    op.drop_table('audit_logs')
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('submission_id', sa.Integer(), sa.ForeignKey('ocr_submission.id'), nullable=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=True),
        sa.Column('action', sa.String(length=64), nullable=True),
        sa.Column('old_text', sa.Text(), nullable=True),
        sa.Column('new_text', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
    )

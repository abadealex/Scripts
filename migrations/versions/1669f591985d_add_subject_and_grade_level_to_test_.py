"""Add subject and grade_level to Test model and replace submission with ocr_submission

Revision ID: 1669f591985d
Revises: 7336e6c2d860
Create Date: 2025-07-21 18:09:22.804027

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1669f591985d'
down_revision = '7336e6c2d860'
branch_labels = None
depends_on = None


def upgrade():
    # Create new ocr_submission table
    op.create_table(
        'ocr_submission',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('image_path', sa.String(length=256), nullable=False),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('needs_human_review', sa.Boolean(), nullable=True),
        sa.Column('manual_override', sa.Boolean(), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['reviewed_by'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Drop foreign key from audit_log to old submission table
    with op.batch_alter_table('audit_log') as batch_op:
        batch_op.drop_constraint('audit_log_submission_id_fkey', type_='foreignkey')

    # Drop old submission table
    op.drop_table('submission')

    # Create foreign key from audit_log to new ocr_submission table
    with op.batch_alter_table('audit_log') as batch_op:
        batch_op.create_foreign_key(
            'audit_log_ocr_submission_fkey',
            'ocr_submission',
            ['submission_id'],
            ['id']
        )

    # Alter marking_guide.test_id: make NOT NULL and add unique constraint
    with op.batch_alter_table('marking_guide') as batch_op:
        batch_op.alter_column('test_id', existing_type=sa.Integer(), nullable=False)
        batch_op.create_unique_constraint('uq_marking_guide_test_id', ['test_id'])

    # Alter student_submissions.test_id: make NOT NULL
    with op.batch_alter_table('student_submissions') as batch_op:
        batch_op.alter_column('test_id', existing_type=sa.Integer(), nullable=False)

    # Add subject and grade_level columns to test table
    with op.batch_alter_table('test') as batch_op:
        batch_op.add_column(sa.Column('subject', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('grade_level', sa.String(length=100), nullable=False))


def downgrade():
    # Remove subject and grade_level columns from test table
    with op.batch_alter_table('test') as batch_op:
        batch_op.drop_column('grade_level')
        batch_op.drop_column('subject')

    # Alter student_submissions.test_id: make nullable
    with op.batch_alter_table('student_submissions') as batch_op:
        batch_op.alter_column('test_id', existing_type=sa.Integer(), nullable=True)

    # Drop unique constraint and make marking_guide.test_id nullable
    with op.batch_alter_table('marking_guide') as batch_op:
        batch_op.drop_constraint('uq_marking_guide_test_id', type_='unique')
        batch_op.alter_column('test_id', existing_type=sa.Integer(), nullable=True)

    # Drop foreign key from audit_log to ocr_submission
    with op.batch_alter_table('audit_log') as batch_op:
        batch_op.drop_constraint('audit_log_ocr_submission_fkey', type_='foreignkey')

    # Recreate old submission table
    op.create_table(
        'submission',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('image_path', sa.String(length=256), nullable=False),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('needs_human_review', sa.Boolean(), nullable=True),
        sa.Column('manual_override', sa.Boolean(), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['reviewed_by'], ['user.id'], name='submission_reviewed_by_fkey'),
        sa.PrimaryKeyConstraint('id', name='submission_pkey')
    )

    # Recreate foreign key from audit_log to submission
    with op.batch_alter_table('audit_log') as batch_op:
        batch_op.create_foreign_key(
            'audit_log_submission_id_fkey',
            'submission',
            ['submission_id'],
            ['id']
        )

    # Drop ocr_submission table
    op.drop_table('ocr_submission')

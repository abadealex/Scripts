"""Rename test file path columns to match template naming

Revision ID: 1bdf8e8ee88a
Revises: 901758acb80f
Create Date: 2025-08-05 01:51:01.442743
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1bdf8e8ee88a'
down_revision = '901758acb80f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('tests') as batch_op:
        batch_op.alter_column('test_pdf_path', new_column_name='question_paper_path')
        batch_op.alter_column('rubric_pdf_path', new_column_name='rubric_path')
        batch_op.alter_column('answer_key_path', new_column_name='marking_guide.filename if marking_guide else None')
        batch_op.alter_column('student_ids_path', new_column_name='class_list_path')


def downgrade():
    with op.batch_alter_table('tests') as batch_op:
        batch_op.alter_column('question_paper_path', new_column_name='test_pdf_path')
        batch_op.alter_column('rubric_path', new_column_name='rubric_pdf_path')
        batch_op.alter_column('marking_guide.filename if marking_guide else None', new_column_name='answer_key_path')
        batch_op.alter_column('class_list_path', new_column_name='student_ids_path')


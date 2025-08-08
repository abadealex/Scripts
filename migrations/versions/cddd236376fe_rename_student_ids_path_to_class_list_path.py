"""Rename student_ids_path to class_list_path and test_pdf_path to question_paper_path

Revision ID: cddd236376fe
Revises: a9cb7ab6f15e
Create Date: 2025-08-05 02:53:25.032256
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'cddd236376fe'
down_revision = 'a9cb7ab6f15e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('tests') as batch_op:
        batch_op.alter_column('student_ids_path', new_column_name='class_list_path')
        batch_op.alter_column('test_pdf_path', new_column_name='question_paper_path')


def downgrade():
    with op.batch_alter_table('tests') as batch_op:
        batch_op.alter_column('class_list_path', new_column_name='student_ids_path')
        batch_op.alter_column('question_paper_path', new_column_name='test_pdf_path')

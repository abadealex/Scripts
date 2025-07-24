"""Initial migration with corrected type casting

Revision ID: e91f72673e22
Revises: 
Create Date: 2025-07-16 20:29:12.613872
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e91f72673e22'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('marking_guide', schema=None) as batch_op:
        batch_op.add_column(sa.Column('test_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'test', ['test_id'], ['id'])

    with op.batch_alter_table('submission_files', schema=None) as batch_op:
        batch_op.alter_column(
            'test_id',
            existing_type=sa.VARCHAR(length=64),
            type_=sa.Integer(),
            existing_nullable=False,
            postgresql_using="test_id::integer"
        )
        batch_op.alter_column(
            'student_id',
            existing_type=sa.VARCHAR(length=64),
            type_=sa.Integer(),
            existing_nullable=False,
            postgresql_using="student_id::integer"
        )
        batch_op.create_foreign_key(None, 'user', ['student_id'], ['id'])
        batch_op.create_foreign_key(None, 'test', ['test_id'], ['id'])


def downgrade():
    with op.batch_alter_table('submission_files', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column(
            'student_id',
            existing_type=sa.Integer(),
            type_=sa.VARCHAR(length=64),
            existing_nullable=False,
            postgresql_using="student_id::varchar"
        )
        batch_op.alter_column(
            'test_id',
            existing_type=sa.Integer(),
            type_=sa.VARCHAR(length=64),
            existing_nullable=False,
            postgresql_using="test_id::varchar"
        )

    with op.batch_alter_table('marking_guide', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('test_id')

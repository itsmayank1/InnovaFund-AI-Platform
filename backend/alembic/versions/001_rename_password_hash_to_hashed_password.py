"""Rename password_hash to hashed_password for shared DB compatibility

Revision ID: 001_password_hash
Revises: 
Create Date: 2026-09-02 16:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001_password_hash'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    try:
        op.alter_column('users', 'password_hash', new_column_name='hashed_password')
    except Exception:
        pass

def downgrade():
    try:
        op.alter_column('users', 'hashed_password', new_column_name='password_hash')
    except Exception:
        pass

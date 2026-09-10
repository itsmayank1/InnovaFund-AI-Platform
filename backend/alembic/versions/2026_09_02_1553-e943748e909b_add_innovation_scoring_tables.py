"""add innovation scoring tables

Revision ID: e943748e909b
Revises: 
Create Date: 2026-09-02 15:53:37.233844

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e943748e909b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Purely additive migration for Member 4 Innovation Scoring tables."""
    # 1. innovation_score_inputs
    op.create_table(
        'innovation_score_inputs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('domain', sa.String(length=100), nullable=True),
        sa.Column('raw_metrics', sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_innovation_score_inputs_id'), 'innovation_score_inputs', ['id'], unique=False)
    op.create_index(op.f('ix_innovation_score_inputs_project_id'), 'innovation_score_inputs', ['project_id'], unique=True)
    op.create_index(op.f('ix_innovation_score_inputs_domain'), 'innovation_score_inputs', ['domain'], unique=False)

    # 2. innovation_score_history
    op.create_table(
        'innovation_score_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.String(length=100), nullable=False),
        sa.Column('model_version', sa.String(length=20), nullable=False, server_default='1.0.0'),
        sa.Column('innovation_score', sa.Float(), nullable=False),
        sa.Column('band', sa.String(length=50), nullable=False),
        sa.Column('pillars', sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'), nullable=False),
        sa.Column('derived_scores', sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'), nullable=False),
        sa.Column('explanation', sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'), nullable=False),
        sa.Column('computed_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_innovation_score_history_id'), 'innovation_score_history', ['id'], unique=False)
    op.create_index(op.f('ix_innovation_score_history_project_id'), 'innovation_score_history', ['project_id'], unique=False)
    op.create_index('idx_score_history_project_time', 'innovation_score_history', ['project_id', 'computed_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema purely reverting innovation scoring tables."""
    op.drop_index('idx_score_history_project_time', table_name='innovation_score_history')
    op.drop_index(op.f('ix_innovation_score_history_project_id'), table_name='innovation_score_history')
    op.drop_index(op.f('ix_innovation_score_history_id'), table_name='innovation_score_history')
    op.drop_table('innovation_score_history')

    op.drop_index(op.f('ix_innovation_score_inputs_domain'), table_name='innovation_score_inputs')
    op.drop_index(op.f('ix_innovation_score_inputs_project_id'), table_name='innovation_score_inputs')
    op.drop_index(op.f('ix_innovation_score_inputs_id'), table_name='innovation_score_inputs')
    op.drop_table('innovation_score_inputs')

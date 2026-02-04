"""Add valor_intermediacao to tabelas_credito

Revision ID: 008
Revises: 007
Create Date: 2026-02-04
"""
from alembic import op
import sqlalchemy as sa


revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tabelas_credito', sa.Column('valor_intermediacao', sa.Numeric(12, 2), server_default='0'))


def downgrade():
    op.drop_column('tabelas_credito', 'valor_intermediacao')

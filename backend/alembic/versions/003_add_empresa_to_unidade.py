"""Add empresa_id to unidades table

Revision ID: 003
Revises: 002
Create Date: 2026-01-26 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adiciona coluna empresa_id na tabela unidades
    op.add_column('unidades', sa.Column('empresa_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_unidades_empresa_id',
        'unidades',
        'empresas',
        ['empresa_id'],
        ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_unidades_empresa_id', 'unidades', type_='foreignkey')
    op.drop_column('unidades', 'empresa_id')

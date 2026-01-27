"""Add permissoes tables

Revision ID: 005
Revises: 004
Create Date: 2026-01-26 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabela de Permissões
    op.create_table(
        'permissoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codigo', sa.String(100), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('modulo', sa.String(50), nullable=False),
        sa.Column('descricao', sa.String(500), nullable=True),
        sa.Column('ativo', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_permissoes_codigo', 'permissoes', ['codigo'], unique=True)

    # Tabela de Perfil-Permissões
    op.create_table(
        'perfil_permissoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('perfil', sa.String(20), nullable=False),
        sa.Column('permissao_id', sa.Integer(), sa.ForeignKey('permissoes.id'), nullable=False),
        sa.Column('ativo', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_perfil_permissoes_perfil', 'perfil_permissoes', ['perfil'])


def downgrade() -> None:
    op.drop_table('perfil_permissoes')
    op.drop_table('permissoes')

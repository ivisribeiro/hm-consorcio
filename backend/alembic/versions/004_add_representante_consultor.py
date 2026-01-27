"""Add representante and consultor tables

Revision ID: 004
Revises: 003
Create Date: 2026-01-26 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabela de Representantes
    op.create_table(
        'representantes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('cpf', sa.String(14), nullable=False),
        sa.Column('telefone', sa.String(20), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('cnpj', sa.String(18), nullable=False),
        sa.Column('razao_social', sa.String(255), nullable=False),
        sa.Column('nome_fantasia', sa.String(255), nullable=True),
        sa.Column('unidade_id', sa.Integer(), sa.ForeignKey('unidades.id'), nullable=False),
        sa.Column('ativo', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_representantes_cpf', 'representantes', ['cpf'])
    op.create_index('ix_representantes_cnpj', 'representantes', ['cnpj'])

    # Tabela de Consultores
    op.create_table(
        'consultores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('cpf', sa.String(14), nullable=False),
        sa.Column('telefone', sa.String(20), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('representante_id', sa.Integer(), sa.ForeignKey('representantes.id'), nullable=False),
        sa.Column('ativo', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_consultores_cpf', 'consultores', ['cpf'])


def downgrade() -> None:
    op.drop_table('consultores')
    op.drop_table('representantes')

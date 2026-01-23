"""Initial tables

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabela de Unidades
    op.create_table(
        'unidades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('codigo', sa.String(50), nullable=False),
        sa.Column('endereco', sa.String(500), nullable=True),
        sa.Column('cidade', sa.String(100), nullable=True),
        sa.Column('estado', sa.String(2), nullable=True),
        sa.Column('cep', sa.String(10), nullable=True),
        sa.Column('telefone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('ativo', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_unidades_codigo', 'unidades', ['codigo'], unique=True)

    # Tabela de Empresas
    op.create_table(
        'empresas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('razao_social', sa.String(255), nullable=False),
        sa.Column('nome_fantasia', sa.String(255), nullable=True),
        sa.Column('cnpj', sa.String(18), nullable=False),
        sa.Column('inscricao_estadual', sa.String(50), nullable=True),
        sa.Column('endereco', sa.String(500), nullable=True),
        sa.Column('cidade', sa.String(100), nullable=True),
        sa.Column('estado', sa.String(2), nullable=True),
        sa.Column('cep', sa.String(10), nullable=True),
        sa.Column('telefone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('ativo', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_empresas_cnpj', 'empresas', ['cnpj'], unique=True)

    # Tabela de Usuários
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('senha_hash', sa.String(255), nullable=False),
        sa.Column('cpf', sa.String(14), nullable=True),
        sa.Column('telefone', sa.String(20), nullable=True),
        sa.Column('perfil', sa.Enum('admin', 'gerente', 'representante', 'consultor', name='perfilusuario'),
                  default='representante', nullable=False),
        sa.Column('ativo', sa.Boolean(), default=True),
        sa.Column('unidade_id', sa.Integer(), sa.ForeignKey('unidades.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_usuarios_email', 'usuarios', ['email'], unique=True)
    op.create_index('ix_usuarios_cpf', 'usuarios', ['cpf'], unique=True)


def downgrade() -> None:
    op.drop_table('usuarios')
    op.drop_table('empresas')
    op.drop_table('unidades')
    op.execute('DROP TYPE IF EXISTS perfilusuario')

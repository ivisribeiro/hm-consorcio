"""Add perfis table and update usuarios

Revision ID: 006
Revises: 005
Create Date: 2026-01-27 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Criar tabela de Perfis (completa)
    op.create_table(
        'perfis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codigo', sa.String(50), nullable=False),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('cor', sa.String(7), nullable=True, server_default='#1890ff'),
        sa.Column('is_system', sa.Boolean(), default=False),
        sa.Column('ativo', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_perfis_codigo', 'perfis', ['codigo'], unique=True)

    # 2. Inserir perfis padrão do sistema
    op.execute("""
        INSERT INTO perfis (id, codigo, nome, descricao, cor, is_system, ativo) VALUES
        (1, 'admin', 'Administrador', 'Acesso total ao sistema', '#f5222d', true, true),
        (2, 'gerente', 'Gerente', 'Gerente de unidade', '#fa8c16', true, true),
        (3, 'vendedor', 'Vendedor', 'Vendedor/Representante', '#1890ff', true, true),
        (4, 'consultor', 'Consultor', 'Consultor de vendas', '#52c41a', true, true)
    """)

    # 3. Adicionar coluna perfil_id em usuarios (nullable primeiro)
    op.add_column('usuarios', sa.Column('perfil_id', sa.Integer(), nullable=True))

    # 4. Migrar dados: converter perfil enum para perfil_id
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('usuarios')]

    if 'perfil' in columns:
        op.execute("""
            UPDATE usuarios SET perfil_id =
                CASE perfil
                    WHEN 'admin' THEN 1
                    WHEN 'gerente' THEN 2
                    WHEN 'vendedor' THEN 3
                    WHEN 'representante' THEN 3
                    WHEN 'consultor' THEN 4
                    ELSE 3
                END
        """)
        # 5. Remover coluna antiga
        op.drop_column('usuarios', 'perfil')
    else:
        # Se não existe coluna perfil, apenas setar padrão
        op.execute("UPDATE usuarios SET perfil_id = 1 WHERE perfil_id IS NULL")

    # 6. Tornar perfil_id NOT NULL e adicionar FK
    op.alter_column('usuarios', 'perfil_id', nullable=False)
    op.create_foreign_key('fk_usuarios_perfil_id', 'usuarios', 'perfis', ['perfil_id'], ['id'])


def downgrade() -> None:
    # Remover FK e coluna
    op.drop_constraint('fk_usuarios_perfil_id', 'usuarios', type_='foreignkey')

    # Adicionar coluna enum de volta
    op.add_column('usuarios', sa.Column('perfil', sa.String(20), nullable=True))

    # Migrar de volta
    op.execute("""
        UPDATE usuarios SET perfil =
            CASE perfil_id
                WHEN 1 THEN 'admin'
                WHEN 2 THEN 'gerente'
                WHEN 3 THEN 'vendedor'
                WHEN 4 THEN 'consultor'
                ELSE 'vendedor'
            END
    """)

    op.alter_column('usuarios', 'perfil', nullable=False)
    op.drop_column('usuarios', 'perfil_id')

    # Remover tabela perfis
    op.drop_index('ix_perfis_codigo', 'perfis')
    op.drop_table('perfis')

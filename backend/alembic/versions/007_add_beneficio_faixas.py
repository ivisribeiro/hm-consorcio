"""Add beneficio_faixas table

Revision ID: 007
Revises: 006_add_perfis_table
Create Date: 2026-02-04
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007_add_beneficio_faixas'
down_revision = '006_add_perfis_table'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'beneficio_faixas',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('beneficio_id', sa.Integer(), sa.ForeignKey('beneficios.id'), nullable=False),
        sa.Column('parcela_inicio', sa.Integer(), nullable=False),
        sa.Column('parcela_fim', sa.Integer(), nullable=False),
        sa.Column('perc_fundo_comum', sa.Numeric(8, 4), nullable=False, server_default='0'),
        sa.Column('perc_administracao', sa.Numeric(8, 4), nullable=False, server_default='0'),
        sa.Column('perc_reserva', sa.Numeric(8, 4), nullable=False, server_default='0'),
        sa.Column('perc_seguro', sa.Numeric(8, 4), nullable=False, server_default='0'),
        sa.Column('valor_parcela', sa.Numeric(12, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_beneficio_faixas_id', 'beneficio_faixas', ['id'])
    op.create_index('ix_beneficio_faixas_beneficio_id', 'beneficio_faixas', ['beneficio_id'])


def downgrade():
    op.drop_index('ix_beneficio_faixas_beneficio_id')
    op.drop_index('ix_beneficio_faixas_id')
    op.drop_table('beneficio_faixas')

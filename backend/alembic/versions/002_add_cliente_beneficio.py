"""Add cliente and beneficio tables

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabela de Clientes
    op.create_table(
        'clientes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('natureza', sa.String(20), default='fisica', nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('cpf', sa.String(14), nullable=False),
        sa.Column('identidade', sa.String(20), nullable=True),
        sa.Column('orgao_expedidor', sa.String(20), nullable=True),
        sa.Column('data_expedicao', sa.Date(), nullable=True),
        sa.Column('sexo', sa.String(20), nullable=True),
        sa.Column('data_nascimento', sa.Date(), nullable=True),
        sa.Column('nacionalidade', sa.String(100), default='Brasileira'),
        sa.Column('naturalidade', sa.String(100), nullable=True),
        sa.Column('nome_mae', sa.String(255), nullable=True),
        sa.Column('nome_pai', sa.String(255), nullable=True),
        sa.Column('estado_civil', sa.String(20), nullable=True),
        sa.Column('conjuge_nome', sa.String(255), nullable=True),
        sa.Column('conjuge_data_nascimento', sa.Date(), nullable=True),
        sa.Column('conjuge_cpf', sa.String(14), nullable=True),
        sa.Column('telefone', sa.String(20), nullable=False),
        sa.Column('telefone_secundario', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('cep', sa.String(10), nullable=True),
        sa.Column('logradouro', sa.String(255), nullable=True),
        sa.Column('numero', sa.String(20), nullable=True),
        sa.Column('complemento', sa.String(100), nullable=True),
        sa.Column('bairro', sa.String(100), nullable=True),
        sa.Column('cidade', sa.String(100), nullable=True),
        sa.Column('estado', sa.String(2), nullable=True),
        sa.Column('tem_consorcio', sa.Boolean(), default=False),
        sa.Column('consorcio_prazo', sa.Integer(), nullable=True),
        sa.Column('consorcio_valor', sa.Numeric(12, 2), nullable=True),
        sa.Column('tem_emprestimo_contracheque', sa.Boolean(), default=False),
        sa.Column('emprestimo_contracheque_prazo', sa.Integer(), nullable=True),
        sa.Column('emprestimo_contracheque_valor', sa.Numeric(12, 2), nullable=True),
        sa.Column('tem_emprestimo_outros', sa.Boolean(), default=False),
        sa.Column('emprestimo_outros_prazo', sa.Integer(), nullable=True),
        sa.Column('emprestimo_outros_valor', sa.Numeric(12, 2), nullable=True),
        sa.Column('tem_financiamento_estudantil', sa.Boolean(), default=False),
        sa.Column('financiamento_estudantil_prazo', sa.Integer(), nullable=True),
        sa.Column('financiamento_estudantil_valor', sa.Numeric(12, 2), nullable=True),
        sa.Column('tem_financiamento_veicular', sa.Boolean(), default=False),
        sa.Column('financiamento_veicular_prazo', sa.Integer(), nullable=True),
        sa.Column('financiamento_veicular_valor', sa.Numeric(12, 2), nullable=True),
        sa.Column('tem_financiamento_habitacional', sa.Boolean(), default=False),
        sa.Column('financiamento_habitacional_prazo', sa.Integer(), nullable=True),
        sa.Column('financiamento_habitacional_valor', sa.Numeric(12, 2), nullable=True),
        sa.Column('tem_aluguel', sa.Boolean(), default=False),
        sa.Column('aluguel_valor', sa.Numeric(12, 2), nullable=True),
        sa.Column('tem_outras_dividas', sa.Boolean(), default=False),
        sa.Column('outras_dividas_valor', sa.Numeric(12, 2), nullable=True),
        sa.Column('possui_restricao', sa.Boolean(), default=False),
        sa.Column('tentou_credito_12_meses', sa.Boolean(), default=False),
        sa.Column('empresa_trabalho', sa.String(255), nullable=True),
        sa.Column('cargo', sa.String(100), nullable=True),
        sa.Column('salario', sa.Numeric(12, 2), nullable=True),
        sa.Column('parcela_maxima', sa.Numeric(12, 2), nullable=True),
        sa.Column('valor_carta_desejado', sa.Numeric(12, 2), nullable=True),
        sa.Column('taxa_inicial', sa.Numeric(5, 2), nullable=True),
        sa.Column('banco', sa.String(100), nullable=True),
        sa.Column('chave_pix', sa.String(255), nullable=True),
        sa.Column('tipo_conta', sa.String(20), nullable=True),
        sa.Column('agencia', sa.String(20), nullable=True),
        sa.Column('conta', sa.String(30), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('unidade_id', sa.Integer(), sa.ForeignKey('unidades.id'), nullable=False),
        sa.Column('empresa_id', sa.Integer(), sa.ForeignKey('empresas.id'), nullable=True),
        sa.Column('representante_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('consultor_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('ativo', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_clientes_cpf', 'clientes', ['cpf'], unique=True)
    op.create_index('ix_clientes_nome', 'clientes', ['nome'])

    # Tabela de Administradoras
    op.create_table(
        'administradoras',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('cnpj', sa.String(18), nullable=False),
        sa.Column('endereco', sa.String(500), nullable=True),
        sa.Column('cidade', sa.String(100), nullable=True),
        sa.Column('estado', sa.String(2), nullable=True),
        sa.Column('telefone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('site', sa.String(255), nullable=True),
        sa.Column('contato_nome', sa.String(255), nullable=True),
        sa.Column('contato_telefone', sa.String(20), nullable=True),
        sa.Column('ativo', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_administradoras_cnpj', 'administradoras', ['cnpj'], unique=True)

    # Tabela de Crédito
    op.create_table(
        'tabelas_credito',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('tipo_bem', sa.String(20), nullable=False),
        sa.Column('prazo', sa.Integer(), nullable=False),
        sa.Column('valor_credito', sa.Numeric(12, 2), nullable=False),
        sa.Column('parcela', sa.Numeric(12, 2), nullable=False),
        sa.Column('fundo_reserva', sa.Numeric(5, 2), default=2.5),
        sa.Column('taxa_administracao', sa.Numeric(5, 2), default=26.0),
        sa.Column('seguro_prestamista', sa.Numeric(5, 2), default=0.0),
        sa.Column('indice_correcao', sa.String(20), default='INCC'),
        sa.Column('qtd_participantes', sa.Integer(), default=4076),
        sa.Column('tipo_plano', sa.String(50), default='Normal'),
        sa.Column('ativo', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tabelas_credito_tipo_bem', 'tabelas_credito', ['tipo_bem'])

    # Tabela de Benefícios
    op.create_table(
        'beneficios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), sa.ForeignKey('clientes.id'), nullable=False),
        sa.Column('representante_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('consultor_id', sa.Integer(), sa.ForeignKey('usuarios.id'), nullable=True),
        sa.Column('unidade_id', sa.Integer(), sa.ForeignKey('unidades.id'), nullable=False),
        sa.Column('empresa_id', sa.Integer(), sa.ForeignKey('empresas.id'), nullable=True),
        sa.Column('tabela_credito_id', sa.Integer(), sa.ForeignKey('tabelas_credito.id'), nullable=False),
        sa.Column('administradora_id', sa.Integer(), sa.ForeignKey('administradoras.id'), nullable=True),
        sa.Column('tipo_bem', sa.String(20), nullable=False),
        sa.Column('prazo_grupo', sa.Integer(), nullable=False),
        sa.Column('valor_credito', sa.Numeric(12, 2), nullable=False),
        sa.Column('parcela', sa.Numeric(12, 2), nullable=False),
        sa.Column('fundo_reserva', sa.Numeric(5, 2), nullable=False),
        sa.Column('taxa_administracao', sa.Numeric(5, 2), default=26.0),
        sa.Column('seguro_prestamista', sa.Numeric(5, 2), default=0.0),
        sa.Column('indice_correcao', sa.String(20), default='INCC'),
        sa.Column('valor_demais_parcelas', sa.Numeric(12, 2), nullable=True),
        sa.Column('qtd_participantes', sa.Integer(), default=4076),
        sa.Column('tipo_plano', sa.String(50), default='Normal'),
        sa.Column('grupo', sa.String(50), nullable=True),
        sa.Column('cota', sa.String(50), nullable=True),
        sa.Column('status', sa.String(30), default='rascunho', nullable=False),
        sa.Column('data_proposta', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_aceite', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_rejeicao', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_contrato', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_assinatura_contrato', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_cadastro_administradora', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_termo', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_assinatura_termo', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_ativacao', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_cancelamento', sa.DateTime(timezone=True), nullable=True),
        sa.Column('motivo_rejeicao', sa.Text(), nullable=True),
        sa.Column('motivo_cancelamento', sa.Text(), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_beneficios_status', 'beneficios', ['status'])


def downgrade() -> None:
    op.drop_table('beneficios')
    op.drop_table('tabelas_credito')
    op.drop_table('administradoras')
    op.drop_table('clientes')

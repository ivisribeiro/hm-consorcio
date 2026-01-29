from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)

    # Dados Básicos
    natureza = Column(String(20), default="fisica", nullable=False)  # fisica, juridica
    nome = Column(String(255), nullable=False, index=True)
    cpf = Column(String(14), unique=True, index=True, nullable=False)
    identidade = Column(String(20), nullable=True)
    orgao_expedidor = Column(String(20), nullable=True)
    data_expedicao = Column(Date, nullable=True)
    sexo = Column(String(20), nullable=True)  # feminino, masculino, outro
    data_nascimento = Column(Date, nullable=True)
    nacionalidade = Column(String(100), default="Brasileira")
    naturalidade = Column(String(100), nullable=True)
    nome_mae = Column(String(255), nullable=True)
    nome_pai = Column(String(255), nullable=True)
    estado_civil = Column(String(20), nullable=True)  # solteiro, casado, divorciado, viuvo, uniao_estavel

    # Dados do Cônjuge
    conjuge_nome = Column(String(255), nullable=True)
    conjuge_data_nascimento = Column(Date, nullable=True)
    conjuge_cpf = Column(String(14), nullable=True)

    # Contato
    telefone = Column(String(20), nullable=False)
    telefone_secundario = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)

    # Endereço
    cep = Column(String(10), nullable=True)
    logradouro = Column(String(255), nullable=True)
    numero = Column(String(20), nullable=True)
    complemento = Column(String(100), nullable=True)
    bairro = Column(String(100), nullable=True)
    cidade = Column(String(100), nullable=True)
    estado = Column(String(2), nullable=True)

    # Compromissos Financeiros
    tem_consorcio = Column(Boolean, default=False)
    consorcio_prazo = Column(Integer, nullable=True)
    consorcio_valor = Column(Numeric(12, 2), nullable=True)

    tem_emprestimo_contracheque = Column(Boolean, default=False)
    emprestimo_contracheque_prazo = Column(Integer, nullable=True)
    emprestimo_contracheque_valor = Column(Numeric(12, 2), nullable=True)

    tem_emprestimo_outros = Column(Boolean, default=False)
    emprestimo_outros_prazo = Column(Integer, nullable=True)
    emprestimo_outros_valor = Column(Numeric(12, 2), nullable=True)

    tem_financiamento_estudantil = Column(Boolean, default=False)
    financiamento_estudantil_prazo = Column(Integer, nullable=True)
    financiamento_estudantil_valor = Column(Numeric(12, 2), nullable=True)

    tem_financiamento_veicular = Column(Boolean, default=False)
    financiamento_veicular_prazo = Column(Integer, nullable=True)
    financiamento_veicular_valor = Column(Numeric(12, 2), nullable=True)

    tem_financiamento_habitacional = Column(Boolean, default=False)
    financiamento_habitacional_prazo = Column(Integer, nullable=True)
    financiamento_habitacional_valor = Column(Numeric(12, 2), nullable=True)

    tem_aluguel = Column(Boolean, default=False)
    aluguel_valor = Column(Numeric(12, 2), nullable=True)

    tem_outras_dividas = Column(Boolean, default=False)
    outras_dividas_valor = Column(Numeric(12, 2), nullable=True)

    possui_restricao = Column(Boolean, default=False)
    tentou_credito_12_meses = Column(Boolean, default=False)

    # Dados Profissionais
    empresa_trabalho = Column(String(255), nullable=True)
    cargo = Column(String(100), nullable=True)
    salario = Column(Numeric(12, 2), nullable=True)

    # Preferências do Cliente
    parcela_maxima = Column(Numeric(12, 2), nullable=True)
    valor_carta_desejado = Column(Numeric(12, 2), nullable=True)
    taxa_inicial = Column(Numeric(12, 2), nullable=True)

    # Dados Bancários
    banco = Column(String(100), nullable=True)
    chave_pix = Column(String(255), nullable=True)
    tipo_conta = Column(String(20), nullable=True)  # corrente, poupanca
    agencia = Column(String(20), nullable=True)
    conta = Column(String(30), nullable=True)

    # Observações
    observacoes = Column(Text, nullable=True)

    # Relacionamentos
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    unidade = relationship("Unidade", backref="clientes")

    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    empresa = relationship("Empresa", backref="clientes")

    representante_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    representante = relationship("Usuario", foreign_keys=[representante_id], backref="clientes_atendidos")

    consultor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    consultor = relationship("Usuario", foreign_keys=[consultor_id], backref="clientes_agendados")

    # Controle
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Cliente {self.nome}>"

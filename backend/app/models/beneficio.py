from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Beneficio(Base):
    __tablename__ = "beneficios"

    id = Column(Integer, primary_key=True, index=True)

    # Relacionamentos principais
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    cliente = relationship("Cliente", backref="beneficios")

    representante_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    representante = relationship("Usuario", foreign_keys=[representante_id], backref="beneficios_vendidos")

    consultor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    consultor = relationship("Usuario", foreign_keys=[consultor_id], backref="beneficios_agendados")

    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    unidade = relationship("Unidade", backref="beneficios")

    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    empresa = relationship("Empresa", backref="beneficios")

    tabela_credito_id = Column(Integer, ForeignKey("tabelas_credito.id"), nullable=False)
    tabela_credito = relationship("TabelaCredito", backref="beneficios")

    administradora_id = Column(Integer, ForeignKey("administradoras.id"), nullable=True)
    administradora = relationship("Administradora", backref="beneficios")

    # Dados do Benefício
    tipo_bem = Column(String(20), nullable=False)  # imovel, carro, moto
    prazo_grupo = Column(Integer, nullable=False)
    valor_credito = Column(Numeric(12, 2), nullable=False)
    parcela = Column(Numeric(12, 2), nullable=False)
    fundo_reserva = Column(Numeric(5, 2), nullable=False)
    taxa_administracao = Column(Numeric(5, 2), default=26.0)
    seguro_prestamista = Column(Numeric(5, 2), default=0.0)
    indice_correcao = Column(String(20), default="INCC")
    valor_demais_parcelas = Column(Numeric(12, 2), nullable=True)
    qtd_participantes = Column(Integer, default=4076)
    tipo_plano = Column(String(50), default="Normal")

    # Dados da Administradora
    grupo = Column(String(50), nullable=True)
    cota = Column(String(50), nullable=True)

    # Status
    status = Column(String(30), default="rascunho", nullable=False, index=True)

    # Datas importantes
    data_proposta = Column(DateTime(timezone=True), nullable=True)
    data_aceite = Column(DateTime(timezone=True), nullable=True)
    data_rejeicao = Column(DateTime(timezone=True), nullable=True)
    data_contrato = Column(DateTime(timezone=True), nullable=True)
    data_assinatura_contrato = Column(DateTime(timezone=True), nullable=True)
    data_cadastro_administradora = Column(DateTime(timezone=True), nullable=True)
    data_termo = Column(DateTime(timezone=True), nullable=True)
    data_assinatura_termo = Column(DateTime(timezone=True), nullable=True)
    data_ativacao = Column(DateTime(timezone=True), nullable=True)
    data_cancelamento = Column(DateTime(timezone=True), nullable=True)

    # Motivos
    motivo_rejeicao = Column(Text, nullable=True)
    motivo_cancelamento = Column(Text, nullable=True)

    # Observações
    observacoes = Column(Text, nullable=True)

    # Controle
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Beneficio {self.id}>"

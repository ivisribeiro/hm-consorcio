from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Contrato(Base):
    __tablename__ = "contratos"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(50), unique=True, index=True, nullable=False)

    # Relacionamento com Benefício (1:1)
    beneficio_id = Column(Integer, ForeignKey("beneficios.id"), nullable=False, unique=True)
    beneficio = relationship("Beneficio", backref="contrato")

    # Status do contrato
    # gerado -> enviado_assinatura -> assinado -> registrado
    # Pode ser cancelado de qualquer estado (exceto registrado)
    status = Column(String(30), default="gerado", nullable=False, index=True)

    # Snapshot dos valores no momento da geração
    valor_credito = Column(Numeric(12, 2), nullable=False)
    parcela = Column(Numeric(12, 2), nullable=False)
    prazo = Column(Integer, nullable=False)
    taxa_administracao = Column(Numeric(5, 2), nullable=False)
    fundo_reserva = Column(Numeric(5, 2), nullable=False)

    # Datas importantes
    data_geracao = Column(DateTime(timezone=True), server_default=func.now())
    data_envio = Column(DateTime(timezone=True), nullable=True)
    data_assinatura = Column(DateTime(timezone=True), nullable=True)
    data_registro = Column(DateTime(timezone=True), nullable=True)
    data_cancelamento = Column(DateTime(timezone=True), nullable=True)

    # Controle de assinaturas
    assinado_cliente = Column(Boolean, default=False)
    assinado_representante = Column(Boolean, default=False)
    assinado_testemunha1 = Column(Boolean, default=False)
    assinado_testemunha2 = Column(Boolean, default=False)

    # Armazenamento do PDF
    pdf_path = Column(String(500), nullable=True)
    pdf_hash = Column(String(64), nullable=True)

    # Observações
    observacoes = Column(Text, nullable=True)
    motivo_cancelamento = Column(Text, nullable=True)

    # Controle
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Contrato {self.numero}>"

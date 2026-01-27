from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class TabelaCredito(Base):
    __tablename__ = "tabelas_credito"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo_bem = Column(String(20), nullable=False, index=True)  # imovel, carro, moto
    prazo = Column(Integer, nullable=False)
    valor_credito = Column(Numeric(12, 2), nullable=False)
    parcela = Column(Numeric(12, 2), nullable=False)
    fundo_reserva = Column(Numeric(5, 2), default=2.5)
    taxa_administracao = Column(Numeric(5, 2), default=26.0)
    seguro_prestamista = Column(Numeric(5, 2), default=0.0)
    indice_correcao = Column(String(20), default="INCC")
    qtd_participantes = Column(Integer, default=4076)
    tipo_plano = Column(String(50), default="Normal")
    ativo = Column(Boolean, default=True)

    # Relacionamento com Administradora
    administradora_id = Column(Integer, ForeignKey("administradoras.id"), nullable=True, index=True)
    administradora = relationship("Administradora", back_populates="tabelas_credito")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<TabelaCredito {self.nome} - {self.tipo_bem}>"

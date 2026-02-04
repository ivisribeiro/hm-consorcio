from sqlalchemy import Column, Integer, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class BeneficioFaixa(Base):
    __tablename__ = "beneficio_faixas"

    id = Column(Integer, primary_key=True, index=True)
    beneficio_id = Column(Integer, ForeignKey("beneficios.id"), nullable=False)

    parcela_inicio = Column(Integer, nullable=False)
    parcela_fim = Column(Integer, nullable=False)
    perc_fundo_comum = Column(Numeric(8, 4), nullable=False, default=0)
    perc_administracao = Column(Numeric(8, 4), nullable=False, default=0)
    perc_reserva = Column(Numeric(8, 4), nullable=False, default=0)
    perc_seguro = Column(Numeric(8, 4), nullable=False, default=0)
    valor_parcela = Column(Numeric(12, 2), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    beneficio = relationship("Beneficio", backref="faixas")

    def __repr__(self):
        return f"<BeneficioFaixa {self.id} parcelas {self.parcela_inicio}-{self.parcela_fim}>"

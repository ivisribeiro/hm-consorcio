from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class BeneficioHistorico(Base):
    __tablename__ = "beneficio_historicos"

    id = Column(Integer, primary_key=True, index=True)

    beneficio_id = Column(Integer, ForeignKey("beneficios.id"), nullable=False, index=True)
    beneficio = relationship("Beneficio", backref="historicos")

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", backref="historicos_beneficio")

    status_anterior = Column(String(30), nullable=True)
    status_novo = Column(String(30), nullable=False)

    acao = Column(String(50), nullable=False)  # avancou, voltou, rejeitou, cancelou

    observacao = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<BeneficioHistorico {self.id} - {self.acao}>"

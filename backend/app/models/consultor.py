from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Consultor(Base):
    __tablename__ = "consultores"

    id = Column(Integer, primary_key=True, index=True)

    # Dados Pessoais
    nome = Column(String(255), nullable=False)
    cpf = Column(String(14), nullable=False, index=True)
    telefone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)

    # Vínculo
    representante_id = Column(Integer, ForeignKey("representantes.id"), nullable=False)

    # Controle
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    representante = relationship("Representante", back_populates="consultores")

    def __repr__(self):
        return f"<Consultor {self.nome}>"

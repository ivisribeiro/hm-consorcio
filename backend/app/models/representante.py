from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Representante(Base):
    __tablename__ = "representantes"

    id = Column(Integer, primary_key=True, index=True)

    # Dados da Pessoa (Representante)
    nome = Column(String(255), nullable=False)
    cpf = Column(String(14), nullable=False, index=True)
    telefone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)

    # Dados da Empresa (CNPJ que representa)
    cnpj = Column(String(18), nullable=False, index=True)
    razao_social = Column(String(255), nullable=False)
    nome_fantasia = Column(String(255), nullable=True)

    # Vínculo
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)

    # Controle
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    unidade = relationship("Unidade", back_populates="representantes")
    consultores = relationship("Consultor", back_populates="representante")

    def __repr__(self):
        return f"<Representante {self.nome}>"

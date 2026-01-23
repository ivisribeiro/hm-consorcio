from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Unidade(Base):
    __tablename__ = "unidades"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    codigo = Column(String(50), unique=True, index=True, nullable=False)
    endereco = Column(String(500), nullable=True)
    cidade = Column(String(100), nullable=True)
    estado = Column(String(2), nullable=True)
    cep = Column(String(10), nullable=True)
    telefone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    ativo = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    usuarios = relationship("Usuario", back_populates="unidade")

    def __repr__(self):
        return f"<Unidade {self.nome}>"

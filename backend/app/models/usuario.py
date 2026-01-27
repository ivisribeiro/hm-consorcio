from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    cpf = Column(String(14), unique=True, index=True, nullable=True)
    telefone = Column(String(20), nullable=True)
    perfil_id = Column(Integer, ForeignKey("perfis.id"), nullable=False)
    ativo = Column(Boolean, default=True)

    # Relacionamentos
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=True)
    unidade = relationship("Unidade", back_populates="usuarios")
    perfil_obj = relationship("Perfil", back_populates="usuarios")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Usuario {self.email}>"

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Permissao(Base):
    __tablename__ = "permissoes"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(100), unique=True, nullable=False, index=True)
    nome = Column(String(255), nullable=False)
    modulo = Column(String(50), nullable=False)
    descricao = Column(String(500), nullable=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    perfil_permissoes = relationship("PerfilPermissao", back_populates="permissao")

    def __repr__(self):
        return f"<Permissao {self.codigo}>"


class PerfilPermissao(Base):
    __tablename__ = "perfil_permissoes"

    id = Column(Integer, primary_key=True, index=True)
    perfil_id = Column(Integer, ForeignKey("perfis.id"), nullable=False, index=True)
    permissao_id = Column(Integer, ForeignKey("permissoes.id"), nullable=False)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    perfil_obj = relationship("Perfil", back_populates="permissoes")
    permissao = relationship("Permissao", back_populates="perfil_permissoes")

    def __repr__(self):
        return f"<PerfilPermissao {self.perfil_id}:{self.permissao_id}>"

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Perfil(Base):
    __tablename__ = "perfis"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)  # admin, gerente, meu_perfil_custom
    nome = Column(String(100), nullable=False)  # Administrador, Gerente, Meu Perfil Custom
    descricao = Column(Text, nullable=True)
    cor = Column(String(7), nullable=True, default="#1890ff")  # Cor para exibição (hex)
    is_system = Column(Boolean, default=False)  # Perfis do sistema não podem ser excluídos
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    permissoes = relationship("PerfilPermissao", back_populates="perfil_obj", cascade="all, delete-orphan")
    usuarios = relationship("Usuario", back_populates="perfil_obj")

    def __repr__(self):
        return f"<Perfil {self.codigo}>"

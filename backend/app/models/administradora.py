from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Administradora(Base):
    __tablename__ = "administradoras"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    cnpj = Column(String(18), unique=True, index=True, nullable=False)
    endereco = Column(String(500), nullable=True)
    cidade = Column(String(100), nullable=True)
    estado = Column(String(2), nullable=True)
    telefone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    site = Column(String(255), nullable=True)
    contato_nome = Column(String(255), nullable=True)
    contato_telefone = Column(String(20), nullable=True)
    ativo = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Administradora {self.nome}>"

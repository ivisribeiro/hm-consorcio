from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class Configuracao(Base):
    __tablename__ = "configuracoes"

    id = Column(Integer, primary_key=True, index=True)

    # Chave única para cada configuração
    chave = Column(String(100), unique=True, nullable=False, index=True)

    # Valor da configuração (armazenado como texto, JSON para valores complexos)
    valor = Column(Text, nullable=True)

    # Categoria para agrupamento
    categoria = Column(String(50), nullable=False, index=True)  # empresa, pdf, sistema

    # Descrição da configuração
    descricao = Column(String(255), nullable=True)

    # Controle
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Configuracao {self.chave}>"

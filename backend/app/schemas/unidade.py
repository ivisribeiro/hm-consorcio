from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UnidadeBase(BaseModel):
    nome: str
    codigo: str
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None


class UnidadeCreate(UnidadeBase):
    pass


class UnidadeUpdate(BaseModel):
    nome: Optional[str] = None
    codigo: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    ativo: Optional[bool] = None


class UnidadeResponse(UnidadeBase):
    id: int
    ativo: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

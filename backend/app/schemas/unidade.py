from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EmpresaSimples(BaseModel):
    id: int
    razao_social: str
    nome_fantasia: Optional[str] = None

    class Config:
        from_attributes = True


class UnidadeBase(BaseModel):
    nome: str
    codigo: str
    empresa_id: Optional[int] = None
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
    empresa_id: Optional[int] = None
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
    empresa: Optional[EmpresaSimples] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

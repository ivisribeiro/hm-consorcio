from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import re


class EmpresaBase(BaseModel):
    razao_social: str
    nome_fantasia: Optional[str] = None
    cnpj: str
    inscricao_estadual: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj(cls, v):
        cnpj = re.sub(r"\D", "", v)
        if len(cnpj) != 14:
            raise ValueError("CNPJ deve ter 14 dígitos")
        return v


class EmpresaCreate(EmpresaBase):
    pass


class EmpresaUpdate(BaseModel):
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    cnpj: Optional[str] = None
    inscricao_estadual: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    ativo: Optional[bool] = None


class EmpresaResponse(EmpresaBase):
    id: int
    ativo: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

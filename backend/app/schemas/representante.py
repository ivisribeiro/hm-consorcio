from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
import re


class UnidadeSimples(BaseModel):
    id: int
    nome: str
    codigo: str

    class Config:
        from_attributes = True


class ConsultorSimples(BaseModel):
    id: int
    nome: str
    cpf: str
    telefone: str

    class Config:
        from_attributes = True


class RepresentanteBase(BaseModel):
    nome: str
    cpf: str
    telefone: str
    email: Optional[str] = None
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    unidade_id: int

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, v):
        cpf = re.sub(r"\D", "", v)
        if len(cpf) != 11:
            raise ValueError("CPF deve ter 11 dígitos")
        return v

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj(cls, v):
        cnpj = re.sub(r"\D", "", v)
        if len(cnpj) != 14:
            raise ValueError("CNPJ deve ter 14 dígitos")
        return v


class RepresentanteCreate(RepresentanteBase):
    pass


class RepresentanteUpdate(BaseModel):
    nome: Optional[str] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    cnpj: Optional[str] = None
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    unidade_id: Optional[int] = None
    ativo: Optional[bool] = None


class RepresentanteResponse(RepresentanteBase):
    id: int
    ativo: bool
    unidade: Optional[UnidadeSimples] = None
    consultores: Optional[List[ConsultorSimples]] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RepresentanteListResponse(RepresentanteBase):
    id: int
    ativo: bool
    unidade: Optional[UnidadeSimples] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

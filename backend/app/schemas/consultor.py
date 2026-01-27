from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import re


class RepresentanteSimples(BaseModel):
    id: int
    nome: str
    cnpj: str
    razao_social: str

    class Config:
        from_attributes = True


class ConsultorBase(BaseModel):
    nome: str
    cpf: str
    telefone: str
    email: Optional[str] = None
    representante_id: int

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, v):
        cpf = re.sub(r"\D", "", v)
        if len(cpf) != 11:
            raise ValueError("CPF deve ter 11 dígitos")
        return v


class ConsultorCreate(ConsultorBase):
    pass


class ConsultorUpdate(BaseModel):
    nome: Optional[str] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    representante_id: Optional[int] = None
    ativo: Optional[bool] = None


class ConsultorResponse(ConsultorBase):
    id: int
    ativo: bool
    representante: Optional[RepresentanteSimples] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

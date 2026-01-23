from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from app.models.usuario import PerfilUsuario
import re


class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    perfil: PerfilUsuario = PerfilUsuario.REPRESENTANTE
    unidade_id: Optional[int] = None

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, v):
        if v is None:
            return v
        # Remove caracteres não numéricos
        cpf = re.sub(r"\D", "", v)
        if len(cpf) != 11:
            raise ValueError("CPF deve ter 11 dígitos")
        return v

    @field_validator("telefone")
    @classmethod
    def validate_telefone(cls, v):
        if v is None:
            return v
        # Remove caracteres não numéricos
        telefone = re.sub(r"\D", "", v)
        if len(telefone) < 10 or len(telefone) > 11:
            raise ValueError("Telefone inválido")
        return v


class UsuarioCreate(UsuarioBase):
    senha: str

    @field_validator("senha")
    @classmethod
    def validate_senha(cls, v):
        if len(v) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres")
        return v


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    perfil: Optional[PerfilUsuario] = None
    unidade_id: Optional[int] = None
    ativo: Optional[bool] = None
    senha: Optional[str] = None


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    perfil: PerfilUsuario
    ativo: bool
    unidade_id: Optional[int] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UsuarioResponse


class TokenRefresh(BaseModel):
    refresh_token: str

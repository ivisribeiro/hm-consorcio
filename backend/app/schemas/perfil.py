from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PerfilBase(BaseModel):
    codigo: str
    nome: str
    descricao: Optional[str] = None
    cor: Optional[str] = "#1890ff"


class PerfilCreate(PerfilBase):
    permissoes: Optional[List[str]] = []  # Lista de códigos de permissão


class PerfilUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    cor: Optional[str] = None
    ativo: Optional[bool] = None
    permissoes: Optional[List[str]] = None  # Lista de códigos de permissão


class PerfilResponse(PerfilBase):
    id: int
    is_system: bool
    ativo: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PerfilComPermissoes(PerfilResponse):
    permissoes: List[str] = []  # Lista de códigos de permissão

    class Config:
        from_attributes = True

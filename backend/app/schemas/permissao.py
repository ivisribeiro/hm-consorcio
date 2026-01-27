from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PermissaoBase(BaseModel):
    codigo: str
    nome: str
    modulo: str
    descricao: Optional[str] = None


class PermissaoCreate(PermissaoBase):
    pass


class PermissaoResponse(PermissaoBase):
    id: int
    ativo: bool

    class Config:
        from_attributes = True


class PerfilSimples(BaseModel):
    id: int
    codigo: str
    nome: str
    cor: Optional[str] = None

    class Config:
        from_attributes = True


class PerfilPermissoesUpdate(BaseModel):
    permissoes: List[str]  # Lista de códigos de permissão


class PermissoesMatriz(BaseModel):
    permissoes: List[PermissaoResponse]
    perfis: List[PerfilSimples]
    matriz: dict  # {perfil_id: [lista de códigos de permissão]}

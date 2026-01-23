from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime


class ConfiguracaoBase(BaseModel):
    chave: str
    valor: Optional[str] = None
    categoria: str
    descricao: Optional[str] = None


class ConfiguracaoCreate(ConfiguracaoBase):
    pass


class ConfiguracaoUpdate(BaseModel):
    valor: Optional[str] = None
    descricao: Optional[str] = None


class ConfiguracaoResponse(ConfiguracaoBase):
    id: int
    ativo: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Configurações estruturadas por categoria
class EmpresaSettings(BaseModel):
    nome: Optional[str] = "HM Capital"
    razao_social: Optional[str] = None
    cnpj: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    site: Optional[str] = None
    logo_url: Optional[str] = None


class PDFSettings(BaseModel):
    cor_header: Optional[str] = "#2E7D32"
    cor_section: Optional[str] = "#E8F5E9"
    show_logo: Optional[bool] = True
    footer_text: Optional[str] = "HM Capital - CRM Consórcios"


class SistemaSettings(BaseModel):
    items_per_page: Optional[int] = 20
    session_timeout_minutes: Optional[int] = 30
    enable_notifications: Optional[bool] = True
    default_currency: Optional[str] = "BRL"

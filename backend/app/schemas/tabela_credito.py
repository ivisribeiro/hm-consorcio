from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class TabelaCreditoBase(BaseModel):
    nome: str
    tipo_bem: str  # imovel, carro, moto
    prazo: int
    valor_credito: Decimal
    parcela: Decimal
    fundo_reserva: Optional[Decimal] = Decimal("2.5")
    taxa_administracao: Optional[Decimal] = Decimal("26.0")
    seguro_prestamista: Optional[Decimal] = Decimal("0.0")
    indice_correcao: Optional[str] = "INCC"
    qtd_participantes: Optional[int] = 4076
    tipo_plano: Optional[str] = "Normal"
    administradora_id: Optional[int] = None


class TabelaCreditoCreate(TabelaCreditoBase):
    pass


class TabelaCreditoUpdate(BaseModel):
    nome: Optional[str] = None
    tipo_bem: Optional[str] = None
    prazo: Optional[int] = None
    valor_credito: Optional[Decimal] = None
    parcela: Optional[Decimal] = None
    fundo_reserva: Optional[Decimal] = None
    taxa_administracao: Optional[Decimal] = None
    seguro_prestamista: Optional[Decimal] = None
    indice_correcao: Optional[str] = None
    qtd_participantes: Optional[int] = None
    tipo_plano: Optional[str] = None
    administradora_id: Optional[int] = None
    ativo: Optional[bool] = None


class TabelaCreditoResponse(TabelaCreditoBase):
    id: int
    ativo: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

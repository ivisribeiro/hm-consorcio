from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal

StatusContrato = Literal["gerado", "enviado_assinatura", "assinado", "registrado", "cancelado"]


class ContratoBase(BaseModel):
    beneficio_id: int
    observacoes: Optional[str] = None


class ContratoCreate(ContratoBase):
    pass


class ContratoUpdate(BaseModel):
    observacoes: Optional[str] = None


class ContratoStatusUpdate(BaseModel):
    status: StatusContrato
    motivo_cancelamento: Optional[str] = None


class ContratoAssinaturaUpdate(BaseModel):
    assinado_cliente: Optional[bool] = None
    assinado_representante: Optional[bool] = None
    assinado_testemunha1: Optional[bool] = None
    assinado_testemunha2: Optional[bool] = None


class BeneficioSimples(BaseModel):
    id: int
    tipo_bem: str
    valor_credito: Decimal
    grupo: Optional[str] = None
    cota: Optional[str] = None

    class Config:
        from_attributes = True


class ClienteSimples(BaseModel):
    id: int
    nome: str
    cpf: str
    telefone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


class ContratoResponse(BaseModel):
    id: int
    numero: str
    beneficio_id: int
    status: str

    valor_credito: Decimal
    parcela: Decimal
    prazo: int
    taxa_administracao: Decimal
    fundo_reserva: Decimal

    data_geracao: Optional[datetime] = None
    data_envio: Optional[datetime] = None
    data_assinatura: Optional[datetime] = None
    data_registro: Optional[datetime] = None
    data_cancelamento: Optional[datetime] = None

    assinado_cliente: bool
    assinado_representante: bool
    assinado_testemunha1: bool
    assinado_testemunha2: bool

    pdf_path: Optional[str] = None
    observacoes: Optional[str] = None
    motivo_cancelamento: Optional[str] = None

    ativo: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Relacionamentos
    beneficio: Optional[BeneficioSimples] = None
    cliente: Optional[ClienteSimples] = None

    class Config:
        from_attributes = True


class ContratoListResponse(BaseModel):
    id: int
    numero: str
    beneficio_id: int
    cliente_nome: Optional[str] = None
    cliente_cpf: Optional[str] = None
    valor_credito: Decimal
    status: str
    data_geracao: Optional[datetime] = None
    data_assinatura: Optional[datetime] = None

    class Config:
        from_attributes = True

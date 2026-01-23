from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal

# Types for validation (using Literal instead of Enum since model uses strings)
TipoBem = Literal["imovel", "carro", "moto"]
StatusBeneficio = Literal[
    "rascunho", "proposto", "aceito", "rejeitado",
    "contrato_gerado", "contrato_assinado", "cadastro_administradora",
    "termo_gerado", "termo_assinado", "ativado", "cancelado"
]


class BeneficioBase(BaseModel):
    cliente_id: int
    tabela_credito_id: int
    unidade_id: int
    representante_id: int
    consultor_id: Optional[int] = None
    empresa_id: Optional[int] = None
    observacoes: Optional[str] = None


class BeneficioCreate(BeneficioBase):
    pass


class BeneficioUpdate(BaseModel):
    observacoes: Optional[str] = None
    administradora_id: Optional[int] = None
    grupo: Optional[str] = None
    cota: Optional[str] = None


class BeneficioStatusUpdate(BaseModel):
    status: StatusBeneficio
    motivo_rejeicao: Optional[str] = None
    motivo_cancelamento: Optional[str] = None


class BeneficioResponse(BaseModel):
    id: int
    cliente_id: int
    representante_id: int
    consultor_id: Optional[int] = None
    unidade_id: int
    empresa_id: Optional[int] = None
    tabela_credito_id: int
    administradora_id: Optional[int] = None

    tipo_bem: TipoBem
    prazo_grupo: int
    valor_credito: Decimal
    parcela: Decimal
    fundo_reserva: Decimal
    taxa_administracao: Decimal
    seguro_prestamista: Decimal
    indice_correcao: str
    valor_demais_parcelas: Optional[Decimal] = None
    qtd_participantes: int
    tipo_plano: str

    grupo: Optional[str] = None
    cota: Optional[str] = None

    status: StatusBeneficio

    data_proposta: Optional[datetime] = None
    data_aceite: Optional[datetime] = None
    data_rejeicao: Optional[datetime] = None
    data_contrato: Optional[datetime] = None
    data_assinatura_contrato: Optional[datetime] = None
    data_cadastro_administradora: Optional[datetime] = None
    data_termo: Optional[datetime] = None
    data_assinatura_termo: Optional[datetime] = None
    data_ativacao: Optional[datetime] = None
    data_cancelamento: Optional[datetime] = None

    motivo_rejeicao: Optional[str] = None
    motivo_cancelamento: Optional[str] = None
    observacoes: Optional[str] = None

    ativo: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BeneficioListResponse(BaseModel):
    id: int
    cliente_id: int
    cliente_nome: Optional[str] = None
    tipo_bem: TipoBem
    valor_credito: Decimal
    parcela: Decimal
    prazo_grupo: int
    status: StatusBeneficio
    grupo: Optional[str] = None
    cota: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TabelaCreditoBase(BaseModel):
    nome: str
    tipo_bem: TipoBem
    prazo: int
    valor_credito: Decimal
    parcela: Decimal
    fundo_reserva: Decimal = Decimal("2.5")
    taxa_administracao: Decimal = Decimal("26.0")
    seguro_prestamista: Decimal = Decimal("0.0")
    indice_correcao: str = "INCC"
    qtd_participantes: int = 4076
    tipo_plano: str = "Normal"


class TabelaCreditoCreate(TabelaCreditoBase):
    pass


class TabelaCreditoUpdate(BaseModel):
    nome: Optional[str] = None
    tipo_bem: Optional[TipoBem] = None
    prazo: Optional[int] = None
    valor_credito: Optional[Decimal] = None
    parcela: Optional[Decimal] = None
    fundo_reserva: Optional[Decimal] = None
    taxa_administracao: Optional[Decimal] = None
    seguro_prestamista: Optional[Decimal] = None
    indice_correcao: Optional[str] = None
    qtd_participantes: Optional[int] = None
    tipo_plano: Optional[str] = None
    ativo: Optional[bool] = None


class TabelaCreditoResponse(TabelaCreditoBase):
    id: int
    ativo: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdministradoraBase(BaseModel):
    nome: str
    cnpj: str
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    site: Optional[str] = None
    contato_nome: Optional[str] = None
    contato_telefone: Optional[str] = None


class AdministradoraCreate(AdministradoraBase):
    pass


class AdministradoraUpdate(BaseModel):
    nome: Optional[str] = None
    cnpj: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    site: Optional[str] = None
    contato_nome: Optional[str] = None
    contato_telefone: Optional[str] = None
    ativo: Optional[bool] = None


class AdministradoraResponse(AdministradoraBase):
    id: int
    ativo: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SimulacaoRequest(BaseModel):
    tipo_bem: TipoBem
    valor_credito_min: Optional[Decimal] = None
    valor_credito_max: Optional[Decimal] = None
    parcela_max: Optional[Decimal] = None


class SimulacaoResponse(BaseModel):
    tabelas: list[TabelaCreditoResponse]

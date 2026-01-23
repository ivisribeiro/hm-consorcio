from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Literal
from datetime import date, datetime
from decimal import Decimal
import re

# Types for validation (using Literal instead of Enum since model uses strings)
NaturezaPessoa = Literal["fisica", "juridica"]
Sexo = Literal["feminino", "masculino", "outro"]
EstadoCivil = Literal["solteiro", "casado", "divorciado", "viuvo", "uniao_estavel"]
TipoConta = Literal["corrente", "poupanca"]


class CompromissosFinanceiros(BaseModel):
    tem_consorcio: bool = False
    consorcio_prazo: Optional[int] = None
    consorcio_valor: Optional[Decimal] = None

    tem_emprestimo_contracheque: bool = False
    emprestimo_contracheque_prazo: Optional[int] = None
    emprestimo_contracheque_valor: Optional[Decimal] = None

    tem_emprestimo_outros: bool = False
    emprestimo_outros_prazo: Optional[int] = None
    emprestimo_outros_valor: Optional[Decimal] = None

    tem_financiamento_estudantil: bool = False
    financiamento_estudantil_prazo: Optional[int] = None
    financiamento_estudantil_valor: Optional[Decimal] = None

    tem_financiamento_veicular: bool = False
    financiamento_veicular_prazo: Optional[int] = None
    financiamento_veicular_valor: Optional[Decimal] = None

    tem_financiamento_habitacional: bool = False
    financiamento_habitacional_prazo: Optional[int] = None
    financiamento_habitacional_valor: Optional[Decimal] = None

    tem_aluguel: bool = False
    aluguel_valor: Optional[Decimal] = None

    tem_outras_dividas: bool = False
    outras_dividas_valor: Optional[Decimal] = None

    possui_restricao: bool = False
    tentou_credito_12_meses: bool = False


class DadosBancarios(BaseModel):
    banco: Optional[str] = None
    chave_pix: Optional[str] = None
    tipo_conta: Optional[TipoConta] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None


class ClienteBase(BaseModel):
    # Dados Básicos
    natureza: NaturezaPessoa = "fisica"
    nome: str
    cpf: str
    identidade: Optional[str] = None
    orgao_expedidor: Optional[str] = None
    data_expedicao: Optional[date] = None
    sexo: Optional[Sexo] = None
    data_nascimento: Optional[date] = None
    nacionalidade: Optional[str] = "Brasileira"
    naturalidade: Optional[str] = None
    nome_mae: Optional[str] = None
    nome_pai: Optional[str] = None
    estado_civil: Optional[EstadoCivil] = None

    # Cônjuge
    conjuge_nome: Optional[str] = None
    conjuge_data_nascimento: Optional[date] = None
    conjuge_cpf: Optional[str] = None

    # Contato
    telefone: str
    telefone_secundario: Optional[str] = None
    email: Optional[EmailStr] = None

    # Endereço
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None

    # Compromissos Financeiros
    tem_consorcio: bool = False
    consorcio_prazo: Optional[int] = None
    consorcio_valor: Optional[Decimal] = None
    tem_emprestimo_contracheque: bool = False
    emprestimo_contracheque_prazo: Optional[int] = None
    emprestimo_contracheque_valor: Optional[Decimal] = None
    tem_emprestimo_outros: bool = False
    emprestimo_outros_prazo: Optional[int] = None
    emprestimo_outros_valor: Optional[Decimal] = None
    tem_financiamento_estudantil: bool = False
    financiamento_estudantil_prazo: Optional[int] = None
    financiamento_estudantil_valor: Optional[Decimal] = None
    tem_financiamento_veicular: bool = False
    financiamento_veicular_prazo: Optional[int] = None
    financiamento_veicular_valor: Optional[Decimal] = None
    tem_financiamento_habitacional: bool = False
    financiamento_habitacional_prazo: Optional[int] = None
    financiamento_habitacional_valor: Optional[Decimal] = None
    tem_aluguel: bool = False
    aluguel_valor: Optional[Decimal] = None
    tem_outras_dividas: bool = False
    outras_dividas_valor: Optional[Decimal] = None
    possui_restricao: bool = False
    tentou_credito_12_meses: bool = False

    # Dados Profissionais
    empresa_trabalho: Optional[str] = None
    cargo: Optional[str] = None
    salario: Optional[Decimal] = None

    # Preferências
    parcela_maxima: Optional[Decimal] = None
    valor_carta_desejado: Optional[Decimal] = None
    taxa_inicial: Optional[Decimal] = None

    # Dados Bancários
    banco: Optional[str] = None
    chave_pix: Optional[str] = None
    tipo_conta: Optional[TipoConta] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None

    # Observações
    observacoes: Optional[str] = None

    # Relacionamentos
    unidade_id: int
    empresa_id: Optional[int] = None
    representante_id: Optional[int] = None
    consultor_id: Optional[int] = None

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, v):
        cpf = re.sub(r"\D", "", v)
        if len(cpf) != 11:
            raise ValueError("CPF deve ter 11 dígitos")
        return v

    @field_validator("telefone", "telefone_secundario")
    @classmethod
    def validate_telefone(cls, v):
        if v is None:
            return v
        telefone = re.sub(r"\D", "", v)
        if len(telefone) < 10 or len(telefone) > 11:
            raise ValueError("Telefone inválido")
        return v


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    natureza: Optional[NaturezaPessoa] = None
    nome: Optional[str] = None
    cpf: Optional[str] = None
    identidade: Optional[str] = None
    orgao_expedidor: Optional[str] = None
    data_expedicao: Optional[date] = None
    sexo: Optional[Sexo] = None
    data_nascimento: Optional[date] = None
    nacionalidade: Optional[str] = None
    naturalidade: Optional[str] = None
    nome_mae: Optional[str] = None
    nome_pai: Optional[str] = None
    estado_civil: Optional[EstadoCivil] = None
    conjuge_nome: Optional[str] = None
    conjuge_data_nascimento: Optional[date] = None
    conjuge_cpf: Optional[str] = None
    telefone: Optional[str] = None
    telefone_secundario: Optional[str] = None
    email: Optional[EmailStr] = None
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    tem_consorcio: Optional[bool] = None
    consorcio_prazo: Optional[int] = None
    consorcio_valor: Optional[Decimal] = None
    tem_emprestimo_contracheque: Optional[bool] = None
    emprestimo_contracheque_prazo: Optional[int] = None
    emprestimo_contracheque_valor: Optional[Decimal] = None
    tem_emprestimo_outros: Optional[bool] = None
    emprestimo_outros_prazo: Optional[int] = None
    emprestimo_outros_valor: Optional[Decimal] = None
    tem_financiamento_estudantil: Optional[bool] = None
    financiamento_estudantil_prazo: Optional[int] = None
    financiamento_estudantil_valor: Optional[Decimal] = None
    tem_financiamento_veicular: Optional[bool] = None
    financiamento_veicular_prazo: Optional[int] = None
    financiamento_veicular_valor: Optional[Decimal] = None
    tem_financiamento_habitacional: Optional[bool] = None
    financiamento_habitacional_prazo: Optional[int] = None
    financiamento_habitacional_valor: Optional[Decimal] = None
    tem_aluguel: Optional[bool] = None
    aluguel_valor: Optional[Decimal] = None
    tem_outras_dividas: Optional[bool] = None
    outras_dividas_valor: Optional[Decimal] = None
    possui_restricao: Optional[bool] = None
    tentou_credito_12_meses: Optional[bool] = None
    empresa_trabalho: Optional[str] = None
    cargo: Optional[str] = None
    salario: Optional[Decimal] = None
    parcela_maxima: Optional[Decimal] = None
    valor_carta_desejado: Optional[Decimal] = None
    taxa_inicial: Optional[Decimal] = None
    banco: Optional[str] = None
    chave_pix: Optional[str] = None
    tipo_conta: Optional[TipoConta] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None
    observacoes: Optional[str] = None
    unidade_id: Optional[int] = None
    empresa_id: Optional[int] = None
    representante_id: Optional[int] = None
    consultor_id: Optional[int] = None
    ativo: Optional[bool] = None


class ClienteResponse(ClienteBase):
    id: int
    ativo: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClienteListResponse(BaseModel):
    id: int
    nome: str
    cpf: str
    telefone: str
    email: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    salario: Optional[Decimal] = None
    ativo: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

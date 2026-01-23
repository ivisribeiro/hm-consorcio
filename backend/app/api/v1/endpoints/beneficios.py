from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Literal
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.beneficio import Beneficio
from app.models.tabela_credito import TabelaCredito
from app.schemas.beneficio import (
    BeneficioCreate, BeneficioUpdate, BeneficioResponse,
    BeneficioListResponse, BeneficioStatusUpdate,
    TabelaCreditoCreate, TabelaCreditoUpdate, TabelaCreditoResponse,
    AdministradoraCreate, AdministradoraUpdate, AdministradoraResponse,
    SimulacaoRequest, SimulacaoResponse
)
from app.models.administradora import Administradora

# Status and type definitions (using strings since model uses String columns)
StatusBeneficio = Literal[
    "rascunho", "proposto", "aceito", "rejeitado",
    "contrato_gerado", "contrato_assinado", "aguardando_cadastro",
    "cadastrado", "termo_gerado", "ativo", "cancelado"
]
TipoBem = Literal["imovel", "carro", "moto"]

router = APIRouter(prefix="/beneficios", tags=["Benefícios"])


# ==================== BENEFÍCIOS ====================

@router.get("/", response_model=List[BeneficioListResponse])
async def list_beneficios(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    cliente_id: Optional[int] = None,
    status: Optional[StatusBeneficio] = None,
    tipo_bem: Optional[TipoBem] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista benefícios com filtros"""
    query = db.query(Beneficio).filter(Beneficio.ativo == True)

    if cliente_id:
        query = query.filter(Beneficio.cliente_id == cliente_id)
    if status:
        query = query.filter(Beneficio.status == status)
    if tipo_bem:
        query = query.filter(Beneficio.tipo_bem == tipo_bem)

    beneficios = query.order_by(Beneficio.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for b in beneficios:
        cliente = db.query(Cliente).filter(Cliente.id == b.cliente_id).first()
        result.append(BeneficioListResponse(
            id=b.id,
            cliente_id=b.cliente_id,
            cliente_nome=cliente.nome if cliente else None,
            tipo_bem=b.tipo_bem,
            valor_credito=b.valor_credito,
            parcela=b.parcela,
            prazo_grupo=b.prazo_grupo,
            status=b.status,
            grupo=b.grupo,
            cota=b.cota,
            created_at=b.created_at
        ))

    return result


@router.post("/", response_model=BeneficioResponse, status_code=status.HTTP_201_CREATED)
async def create_beneficio(
    beneficio_data: BeneficioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria um novo benefício baseado na tabela de crédito"""
    # Verifica se cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == beneficio_data.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Verifica tabela de crédito
    tabela = db.query(TabelaCredito).filter(TabelaCredito.id == beneficio_data.tabela_credito_id).first()
    if not tabela:
        raise HTTPException(status_code=404, detail="Tabela de crédito não encontrada")

    # Validação de capacidade de pagamento (parcela não pode exceder 30% do salário)
    if cliente.salario:
        limite_parcela = float(cliente.salario) * 0.30
        if float(tabela.parcela) > limite_parcela:
            raise HTTPException(
                status_code=400,
                detail=f"Parcela de R$ {tabela.parcela} excede 30% do salário (R$ {limite_parcela:.2f})"
            )

    # Cria benefício com dados da tabela
    beneficio = Beneficio(
        cliente_id=beneficio_data.cliente_id,
        representante_id=beneficio_data.representante_id or current_user.id,
        consultor_id=beneficio_data.consultor_id,
        unidade_id=beneficio_data.unidade_id,
        empresa_id=beneficio_data.empresa_id,
        tabela_credito_id=beneficio_data.tabela_credito_id,
        tipo_bem=tabela.tipo_bem,
        prazo_grupo=tabela.prazo,
        valor_credito=tabela.valor_credito,
        parcela=tabela.parcela,
        fundo_reserva=tabela.fundo_reserva,
        taxa_administracao=tabela.taxa_administracao,
        seguro_prestamista=tabela.seguro_prestamista,
        indice_correcao=tabela.indice_correcao,
        qtd_participantes=tabela.qtd_participantes,
        tipo_plano=tabela.tipo_plano,
        observacoes=beneficio_data.observacoes,
        status="rascunho"
    )

    db.add(beneficio)
    db.commit()
    db.refresh(beneficio)

    return beneficio


@router.get("/{beneficio_id}", response_model=BeneficioResponse)
async def get_beneficio(
    beneficio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém um benefício pelo ID"""
    beneficio = db.query(Beneficio).filter(Beneficio.id == beneficio_id).first()

    if not beneficio:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")

    return beneficio


@router.put("/{beneficio_id}", response_model=BeneficioResponse)
async def update_beneficio(
    beneficio_id: int,
    beneficio_data: BeneficioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza um benefício"""
    beneficio = db.query(Beneficio).filter(Beneficio.id == beneficio_id).first()

    if not beneficio:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")

    update_data = beneficio_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(beneficio, key, value)

    db.commit()
    db.refresh(beneficio)

    return beneficio


@router.patch("/{beneficio_id}/status", response_model=BeneficioResponse)
async def update_beneficio_status(
    beneficio_id: int,
    status_data: BeneficioStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza o status de um benefício seguindo o workflow"""
    beneficio = db.query(Beneficio).filter(Beneficio.id == beneficio_id).first()

    if not beneficio:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")

    # Valida transições de status
    valid_transitions = {
        "rascunho": ["proposto", "cancelado"],
        "proposto": ["aceito", "rejeitado"],
        "aceito": ["contrato_gerado", "cancelado"],
        "contrato_gerado": ["contrato_assinado", "cancelado"],
        "contrato_assinado": ["aguardando_cadastro", "cancelado"],
        "aguardando_cadastro": ["cadastrado", "cancelado"],
        "cadastrado": ["termo_gerado", "cancelado"],
        "termo_gerado": ["ativo", "cancelado"],
    }

    allowed = valid_transitions.get(beneficio.status, [])
    if status_data.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Transição de {beneficio.status} para {status_data.status} não permitida"
        )

    # Atualiza status e datas correspondentes
    beneficio.status = status_data.status
    now = datetime.utcnow()

    if status_data.status == "proposto":
        beneficio.data_proposta = now
    elif status_data.status == "aceito":
        beneficio.data_aceite = now
    elif status_data.status == "rejeitado":
        beneficio.data_rejeicao = now
        beneficio.motivo_rejeicao = status_data.motivo_rejeicao
    elif status_data.status == "contrato_gerado":
        beneficio.data_contrato = now
    elif status_data.status == "contrato_assinado":
        beneficio.data_assinatura_contrato = now
    elif status_data.status == "cadastrado":
        beneficio.data_cadastro_administradora = now
    elif status_data.status == "termo_gerado":
        beneficio.data_termo = now
    elif status_data.status == "ativo":
        beneficio.data_ativacao = now
        beneficio.data_assinatura_termo = now
    elif status_data.status == "cancelado":
        beneficio.data_cancelamento = now
        beneficio.motivo_cancelamento = status_data.motivo_cancelamento

    db.commit()
    db.refresh(beneficio)

    return beneficio


# ==================== TABELAS DE CRÉDITO ====================

@router.get("/tabelas/", response_model=List[TabelaCreditoResponse])
async def list_tabelas_credito(
    tipo_bem: Optional[TipoBem] = None,
    ativo: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista tabelas de crédito"""
    query = db.query(TabelaCredito)

    if tipo_bem:
        query = query.filter(TabelaCredito.tipo_bem == tipo_bem)
    if ativo is not None:
        query = query.filter(TabelaCredito.ativo == ativo)

    return query.order_by(TabelaCredito.valor_credito).all()


@router.post("/tabelas/", response_model=TabelaCreditoResponse, status_code=status.HTTP_201_CREATED)
async def create_tabela_credito(
    tabela_data: TabelaCreditoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria uma nova tabela de crédito"""
    tabela = TabelaCredito(**tabela_data.model_dump())
    db.add(tabela)
    db.commit()
    db.refresh(tabela)
    return tabela


@router.put("/tabelas/{tabela_id}", response_model=TabelaCreditoResponse)
async def update_tabela_credito(
    tabela_id: int,
    tabela_data: TabelaCreditoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza uma tabela de crédito"""
    tabela = db.query(TabelaCredito).filter(TabelaCredito.id == tabela_id).first()

    if not tabela:
        raise HTTPException(status_code=404, detail="Tabela não encontrada")

    update_data = tabela_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tabela, key, value)

    db.commit()
    db.refresh(tabela)
    return tabela


@router.post("/simular", response_model=SimulacaoResponse)
async def simular_beneficio(
    simulacao: SimulacaoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Simula opções de benefício baseado nos critérios"""
    query = db.query(TabelaCredito).filter(
        TabelaCredito.tipo_bem == simulacao.tipo_bem,
        TabelaCredito.ativo == True
    )

    if simulacao.valor_credito_min:
        query = query.filter(TabelaCredito.valor_credito >= simulacao.valor_credito_min)
    if simulacao.valor_credito_max:
        query = query.filter(TabelaCredito.valor_credito <= simulacao.valor_credito_max)
    if simulacao.parcela_max:
        query = query.filter(TabelaCredito.parcela <= simulacao.parcela_max)

    tabelas = query.order_by(TabelaCredito.valor_credito).all()

    return SimulacaoResponse(tabelas=tabelas)


# ==================== ADMINISTRADORAS ====================

@router.get("/administradoras/", response_model=List[AdministradoraResponse])
async def list_administradoras(
    ativo: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista administradoras"""
    query = db.query(Administradora)
    if ativo is not None:
        query = query.filter(Administradora.ativo == ativo)
    return query.all()


@router.post("/administradoras/", response_model=AdministradoraResponse, status_code=status.HTTP_201_CREATED)
async def create_administradora(
    admin_data: AdministradoraCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria uma nova administradora"""
    admin = Administradora(**admin_data.model_dump())
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@router.put("/administradoras/{admin_id}", response_model=AdministradoraResponse)
async def update_administradora(
    admin_id: int,
    admin_data: AdministradoraUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza uma administradora"""
    admin = db.query(Administradora).filter(Administradora.id == admin_id).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Administradora não encontrada")

    update_data = admin_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(admin, key, value)

    db.commit()
    db.refresh(admin)
    return admin

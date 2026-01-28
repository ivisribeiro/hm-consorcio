from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.models.tabela_credito import TabelaCredito
from app.schemas.tabela_credito import TabelaCreditoCreate, TabelaCreditoUpdate, TabelaCreditoResponse

router = APIRouter(prefix="/tabelas-credito", tags=["Tabelas de Crédito"])


@router.get("/", response_model=List[TabelaCreditoResponse])
async def list_tabelas_credito(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tipo_bem: Optional[str] = None,
    ativo: Optional[bool] = True,
    administradora_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista todas as tabelas de crédito"""
    query = db.query(TabelaCredito)

    if tipo_bem:
        query = query.filter(TabelaCredito.tipo_bem == tipo_bem)
    if ativo is not None:
        query = query.filter(TabelaCredito.ativo == ativo)
    if administradora_id:
        query = query.filter(TabelaCredito.administradora_id == administradora_id)

    return query.order_by(TabelaCredito.tipo_bem, TabelaCredito.valor_credito).offset(skip).limit(limit).all()


@router.post("/", response_model=TabelaCreditoResponse, status_code=status.HTTP_201_CREATED)
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


@router.get("/{tabela_id}", response_model=TabelaCreditoResponse)
async def get_tabela_credito(
    tabela_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém uma tabela de crédito pelo ID"""
    tabela = db.query(TabelaCredito).filter(TabelaCredito.id == tabela_id).first()
    if not tabela:
        raise HTTPException(status_code=404, detail="Tabela de crédito não encontrada")
    return tabela


@router.put("/{tabela_id}", response_model=TabelaCreditoResponse)
async def update_tabela_credito(
    tabela_id: int,
    tabela_data: TabelaCreditoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza uma tabela de crédito"""
    tabela = db.query(TabelaCredito).filter(TabelaCredito.id == tabela_id).first()
    if not tabela:
        raise HTTPException(status_code=404, detail="Tabela de crédito não encontrada")

    update_data = tabela_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tabela, key, value)

    db.commit()
    db.refresh(tabela)
    return tabela


@router.delete("/{tabela_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tabela_credito(
    tabela_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Desativa uma tabela de crédito (soft delete)"""
    tabela = db.query(TabelaCredito).filter(TabelaCredito.id == tabela_id).first()
    if not tabela:
        raise HTTPException(status_code=404, detail="Tabela de crédito não encontrada")

    tabela.ativo = False
    db.commit()
    return None

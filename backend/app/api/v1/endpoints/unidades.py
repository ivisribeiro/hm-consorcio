from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.models.unidade import Unidade
from app.schemas.unidade import UnidadeCreate, UnidadeUpdate, UnidadeResponse
from app.api.v1.endpoints.perfis import check_permission

router = APIRouter(prefix="/unidades", tags=["Unidades"])


@router.get("/", response_model=List[UnidadeResponse])
async def list_unidades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    ativo: Optional[bool] = True,
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista todas as unidades"""
    query = db.query(Unidade).options(joinedload(Unidade.empresa))
    if ativo is not None:
        query = query.filter(Unidade.ativo == ativo)
    if empresa_id is not None:
        query = query.filter(Unidade.empresa_id == empresa_id)
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=UnidadeResponse, status_code=status.HTTP_201_CREATED)
async def create_unidade(
    unidade_data: UnidadeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("cadastros.unidades"))
):
    """Cria uma nova unidade"""
    existing = db.query(Unidade).filter(Unidade.codigo == unidade_data.codigo).first()
    if existing:
        raise HTTPException(status_code=400, detail="Código já existe")

    unidade = Unidade(**unidade_data.model_dump())
    db.add(unidade)
    db.commit()
    db.refresh(unidade)
    return unidade


@router.get("/{unidade_id}", response_model=UnidadeResponse)
async def get_unidade(
    unidade_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém uma unidade pelo ID"""
    unidade = db.query(Unidade).options(joinedload(Unidade.empresa)).filter(Unidade.id == unidade_id).first()
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")
    return unidade


@router.put("/{unidade_id}", response_model=UnidadeResponse)
async def update_unidade(
    unidade_id: int,
    unidade_data: UnidadeUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("cadastros.unidades"))
):
    """Atualiza uma unidade"""
    unidade = db.query(Unidade).filter(Unidade.id == unidade_id).first()
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")

    update_data = unidade_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(unidade, key, value)

    db.commit()
    db.refresh(unidade)
    return unidade


@router.delete("/{unidade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_unidade(
    unidade_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("cadastros.unidades"))
):
    """Desativa uma unidade"""
    unidade = db.query(Unidade).filter(Unidade.id == unidade_id).first()
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")

    unidade.ativo = False
    db.commit()
    return None

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.models.consultor import Consultor
from app.schemas.consultor import (
    ConsultorCreate,
    ConsultorUpdate,
    ConsultorResponse
)
from app.api.v1.endpoints.perfis import check_permission

router = APIRouter(prefix="/consultores", tags=["Consultores"])


@router.get("/", response_model=List[ConsultorResponse])
async def list_consultores(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    ativo: Optional[bool] = True,
    representante_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista todos os consultores"""
    query = db.query(Consultor).options(joinedload(Consultor.representante))
    if ativo is not None:
        query = query.filter(Consultor.ativo == ativo)
    if representante_id is not None:
        query = query.filter(Consultor.representante_id == representante_id)
    return query.order_by(Consultor.nome).offset(skip).limit(limit).all()


@router.post("/", response_model=ConsultorResponse, status_code=status.HTTP_201_CREATED)
async def create_consultor(
    consultor_data: ConsultorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("cadastros.consultores"))
):
    """Cria um novo consultor"""
    consultor = Consultor(**consultor_data.model_dump())
    db.add(consultor)
    db.commit()
    db.refresh(consultor)
    return db.query(Consultor).options(
        joinedload(Consultor.representante)
    ).filter(Consultor.id == consultor.id).first()


@router.get("/{consultor_id}", response_model=ConsultorResponse)
async def get_consultor(
    consultor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém um consultor pelo ID"""
    consultor = db.query(Consultor).options(
        joinedload(Consultor.representante)
    ).filter(Consultor.id == consultor_id).first()
    if not consultor:
        raise HTTPException(status_code=404, detail="Consultor não encontrado")
    return consultor


@router.put("/{consultor_id}", response_model=ConsultorResponse)
async def update_consultor(
    consultor_id: int,
    consultor_data: ConsultorUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("cadastros.consultores"))
):
    """Atualiza um consultor"""
    consultor = db.query(Consultor).filter(Consultor.id == consultor_id).first()
    if not consultor:
        raise HTTPException(status_code=404, detail="Consultor não encontrado")

    update_data = consultor_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(consultor, key, value)

    db.commit()
    db.refresh(consultor)
    return db.query(Consultor).options(
        joinedload(Consultor.representante)
    ).filter(Consultor.id == consultor.id).first()


@router.delete("/{consultor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_consultor(
    consultor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("cadastros.consultores"))
):
    """Desativa um consultor"""
    consultor = db.query(Consultor).filter(Consultor.id == consultor_id).first()
    if not consultor:
        raise HTTPException(status_code=404, detail="Consultor não encontrado")

    consultor.ativo = False
    db.commit()
    return None

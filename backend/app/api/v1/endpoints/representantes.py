from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.models.representante import Representante
from app.schemas.representante import (
    RepresentanteCreate,
    RepresentanteUpdate,
    RepresentanteResponse,
    RepresentanteListResponse
)
from app.api.v1.endpoints.perfis import check_permission

router = APIRouter(prefix="/representantes", tags=["Representantes"])


@router.get("/", response_model=List[RepresentanteListResponse])
async def list_representantes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    ativo: Optional[bool] = True,
    unidade_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista todos os representantes"""
    query = db.query(Representante).options(joinedload(Representante.unidade))
    if ativo is not None:
        query = query.filter(Representante.ativo == ativo)
    if unidade_id is not None:
        query = query.filter(Representante.unidade_id == unidade_id)
    return query.order_by(Representante.nome).offset(skip).limit(limit).all()


@router.post("/", response_model=RepresentanteResponse, status_code=status.HTTP_201_CREATED)
async def create_representante(
    representante_data: RepresentanteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("cadastros.representantes"))
):
    """Cria um novo representante"""
    representante = Representante(**representante_data.model_dump())
    db.add(representante)
    db.commit()
    db.refresh(representante)
    return db.query(Representante).options(
        joinedload(Representante.unidade),
        joinedload(Representante.consultores)
    ).filter(Representante.id == representante.id).first()


@router.get("/{representante_id}", response_model=RepresentanteResponse)
async def get_representante(
    representante_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém um representante pelo ID"""
    representante = db.query(Representante).options(
        joinedload(Representante.unidade),
        joinedload(Representante.consultores)
    ).filter(Representante.id == representante_id).first()
    if not representante:
        raise HTTPException(status_code=404, detail="Representante não encontrado")
    return representante


@router.put("/{representante_id}", response_model=RepresentanteResponse)
async def update_representante(
    representante_id: int,
    representante_data: RepresentanteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("cadastros.representantes"))
):
    """Atualiza um representante"""
    representante = db.query(Representante).filter(Representante.id == representante_id).first()
    if not representante:
        raise HTTPException(status_code=404, detail="Representante não encontrado")

    update_data = representante_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(representante, key, value)

    db.commit()
    db.refresh(representante)
    return db.query(Representante).options(
        joinedload(Representante.unidade),
        joinedload(Representante.consultores)
    ).filter(Representante.id == representante.id).first()


@router.delete("/{representante_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_representante(
    representante_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("cadastros.representantes"))
):
    """Desativa um representante"""
    representante = db.query(Representante).filter(Representante.id == representante_id).first()
    if not representante:
        raise HTTPException(status_code=404, detail="Representante não encontrado")

    representante.ativo = False
    db.commit()
    return None

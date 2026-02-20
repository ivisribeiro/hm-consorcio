from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.beneficio import Beneficio
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse, ClienteListResponse

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("/", response_model=List[ClienteListResponse])
async def list_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    unidade_id: Optional[int] = None,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista clientes com paginação e filtros"""
    query = db.query(Cliente)

    if search:
        query = query.filter(
            (Cliente.nome.ilike(f"%{search}%")) |
            (Cliente.cpf.ilike(f"%{search}%")) |
            (Cliente.telefone.ilike(f"%{search}%"))
        )

    if unidade_id:
        query = query.filter(Cliente.unidade_id == unidade_id)

    if ativo is not None:
        query = query.filter(Cliente.ativo == ativo)

    total = query.count()
    clientes = query.order_by(Cliente.created_at.desc()).offset(skip).limit(limit).all()

    return clientes


@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
async def create_cliente(
    cliente_data: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria um novo cliente"""
    # Verifica se CPF já existe
    existing = db.query(Cliente).filter(Cliente.cpf == cliente_data.cpf).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado"
        )

    # Define representante como usuário atual se não informado
    if not cliente_data.representante_id:
        cliente_data.representante_id = current_user.id

    cliente = Cliente(**cliente_data.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    return cliente


@router.get("/{cliente_id}", response_model=ClienteResponse)
async def get_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém um cliente pelo ID"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )

    return cliente


@router.put("/{cliente_id}", response_model=ClienteResponse)
async def update_cliente(
    cliente_id: int,
    cliente_data: ClienteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza um cliente"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )

    # Verifica se CPF já existe em outro cliente
    if cliente_data.cpf:
        existing = db.query(Cliente).filter(
            Cliente.cpf == cliente_data.cpf,
            Cliente.id != cliente_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )

    update_data = cliente_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cliente, key, value)

    db.commit()
    db.refresh(cliente)

    return cliente


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Desativa um cliente (soft delete)"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )

    cliente.ativo = False
    db.commit()

    return None


@router.delete("/{cliente_id}/permanente", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cliente_permanente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Exclui um cliente permanentemente do banco de dados"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )

    # Verifica se tem benefícios vinculados
    beneficios_count = db.query(Beneficio).filter(Beneficio.cliente_id == cliente_id).count()
    if beneficios_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cliente possui {beneficios_count} benefício(s) vinculado(s). Remova os benefícios antes de excluir."
        )

    db.delete(cliente)
    db.commit()

    return None

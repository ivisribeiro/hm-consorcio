from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash
from app.models.usuario import Usuario
from app.models.perfil import Perfil
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse, PerfilInfo
from app.api.v1.endpoints.perfis import check_permission

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


def usuario_to_response(usuario: Usuario) -> UsuarioResponse:
    """Converte usuario para response com perfil info"""
    perfil_info = None
    if usuario.perfil_obj:
        perfil_info = PerfilInfo(
            id=usuario.perfil_obj.id,
            codigo=usuario.perfil_obj.codigo,
            nome=usuario.perfil_obj.nome,
            cor=usuario.perfil_obj.cor
        )

    return UsuarioResponse(
        id=usuario.id,
        nome=usuario.nome,
        email=usuario.email,
        cpf=usuario.cpf,
        telefone=usuario.telefone,
        perfil_id=usuario.perfil_id,
        perfil=perfil_info,
        ativo=usuario.ativo,
        unidade_id=usuario.unidade_id,
        created_at=usuario.created_at,
        last_login=usuario.last_login
    )


@router.get("/", response_model=List[UsuarioResponse])
async def list_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    perfil_id: Optional[int] = None,
    ativo: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("cadastros.usuarios"))
):
    """
    Lista todos os usuários com paginação e filtros
    """
    query = db.query(Usuario).options(joinedload(Usuario.perfil_obj))

    if perfil_id:
        query = query.filter(Usuario.perfil_id == perfil_id)
    if ativo is not None:
        query = query.filter(Usuario.ativo == ativo)
    if search:
        query = query.filter(
            (Usuario.nome.ilike(f"%{search}%")) |
            (Usuario.email.ilike(f"%{search}%"))
        )

    usuarios = query.offset(skip).limit(limit).all()

    return [usuario_to_response(u) for u in usuarios]


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def create_usuario(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("cadastros.usuarios"))
):
    """
    Cria um novo usuário
    """
    # Verifica se email já existe
    if db.query(Usuario).filter(Usuario.email == usuario_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    # Verifica se CPF já existe
    if usuario_data.cpf:
        if db.query(Usuario).filter(Usuario.cpf == usuario_data.cpf).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )

    # Verifica se o perfil existe
    perfil = db.query(Perfil).filter(Perfil.id == usuario_data.perfil_id).first()
    if not perfil:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Perfil não encontrado"
        )

    # Cria usuário
    usuario = Usuario(
        nome=usuario_data.nome,
        email=usuario_data.email,
        senha_hash=get_password_hash(usuario_data.senha),
        cpf=usuario_data.cpf,
        telefone=usuario_data.telefone,
        perfil_id=usuario_data.perfil_id,
        unidade_id=usuario_data.unidade_id
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    # Reload with perfil_obj
    usuario = db.query(Usuario).options(joinedload(Usuario.perfil_obj)).filter(Usuario.id == usuario.id).first()

    return usuario_to_response(usuario)


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def get_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtém um usuário pelo ID
    """
    usuario = db.query(Usuario).options(joinedload(Usuario.perfil_obj)).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    return usuario_to_response(usuario)


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def update_usuario(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("cadastros.usuarios"))
):
    """
    Atualiza um usuário
    """
    usuario = db.query(Usuario).options(joinedload(Usuario.perfil_obj)).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    # Verifica se email já existe em outro usuário
    if usuario_data.email:
        existing = db.query(Usuario).filter(
            Usuario.email == usuario_data.email,
            Usuario.id != usuario_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )

    # Verifica se o perfil existe se foi passado
    if usuario_data.perfil_id:
        perfil = db.query(Perfil).filter(Perfil.id == usuario_data.perfil_id).first()
        if not perfil:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Perfil não encontrado"
            )

    # Atualiza campos
    update_data = usuario_data.model_dump(exclude_unset=True)

    # Hash da senha se foi alterada
    if "senha" in update_data:
        update_data["senha_hash"] = get_password_hash(update_data.pop("senha"))

    for key, value in update_data.items():
        setattr(usuario, key, value)

    db.commit()
    db.refresh(usuario)

    # Reload with perfil_obj
    usuario = db.query(Usuario).options(joinedload(Usuario.perfil_obj)).filter(Usuario.id == usuario.id).first()

    return usuario_to_response(usuario)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission("cadastros.usuarios"))
):
    """
    Desativa um usuário (soft delete)
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    if usuario.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível desativar seu próprio usuário"
        )

    # Soft delete
    usuario.ativo = False
    db.commit()

    return None

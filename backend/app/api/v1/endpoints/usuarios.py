from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash, check_permission
from app.models.usuario import Usuario, PerfilUsuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.get("/", response_model=List[UsuarioResponse])
async def list_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    perfil: Optional[PerfilUsuario] = None,
    ativo: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission([PerfilUsuario.ADMIN, PerfilUsuario.GERENTE]))
):
    """
    Lista todos os usuários com paginação e filtros
    """
    query = db.query(Usuario)

    if perfil:
        query = query.filter(Usuario.perfil == perfil)
    if ativo is not None:
        query = query.filter(Usuario.ativo == ativo)
    if search:
        query = query.filter(
            (Usuario.nome.ilike(f"%{search}%")) |
            (Usuario.email.ilike(f"%{search}%"))
        )

    total = query.count()
    usuarios = query.offset(skip).limit(limit).all()

    return usuarios


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def create_usuario(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission([PerfilUsuario.ADMIN]))
):
    """
    Cria um novo usuário (apenas Admin)
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

    # Cria usuário
    usuario = Usuario(
        nome=usuario_data.nome,
        email=usuario_data.email,
        senha_hash=get_password_hash(usuario_data.senha),
        cpf=usuario_data.cpf,
        telefone=usuario_data.telefone,
        perfil=usuario_data.perfil,
        unidade_id=usuario_data.unidade_id
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return UsuarioResponse.model_validate(usuario)


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def get_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtém um usuário pelo ID
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    return UsuarioResponse.model_validate(usuario)


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def update_usuario(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission([PerfilUsuario.ADMIN]))
):
    """
    Atualiza um usuário (apenas Admin)
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

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

    # Atualiza campos
    update_data = usuario_data.model_dump(exclude_unset=True)

    # Hash da senha se foi alterada
    if "senha" in update_data:
        update_data["senha_hash"] = get_password_hash(update_data.pop("senha"))

    for key, value in update_data.items():
        setattr(usuario, key, value)

    db.commit()
    db.refresh(usuario)

    return UsuarioResponse.model_validate(usuario)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permission([PerfilUsuario.ADMIN]))
):
    """
    Desativa um usuário (soft delete) - apenas Admin
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

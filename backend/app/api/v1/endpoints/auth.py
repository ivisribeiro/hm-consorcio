from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.core.database import get_db
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user
)
from app.models.usuario import Usuario
from app.schemas.usuario import Token, TokenRefresh, UsuarioResponse, PerfilInfo

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def build_usuario_response(user: Usuario) -> UsuarioResponse:
    """Helper para construir UsuarioResponse com perfil"""
    perfil_info = None
    if user.perfil_obj:
        perfil_info = PerfilInfo(
            id=user.perfil_obj.id,
            codigo=user.perfil_obj.codigo,
            nome=user.perfil_obj.nome,
            cor=user.perfil_obj.cor
        )
    return UsuarioResponse(
        id=user.id,
        nome=user.nome,
        email=user.email,
        cpf=user.cpf,
        telefone=user.telefone,
        perfil_id=user.perfil_id,
        perfil=perfil_info,
        ativo=user.ativo,
        unidade_id=user.unidade_id,
        created_at=user.created_at,
        last_login=user.last_login
    )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Realiza login do usuário e retorna tokens JWT
    """
    # Busca usuário pelo email com perfil
    user = db.query(Usuario).options(
        joinedload(Usuario.perfil_obj)
    ).filter(Usuario.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    # Atualiza último login
    user.last_login = datetime.utcnow()
    db.commit()

    # Cria tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        user=build_usuario_response(user)
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Renova o access token usando o refresh token
    """
    payload = decode_token(token_data.refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresh inválido"
        )

    user_id = payload.get("sub")
    user = db.query(Usuario).options(
        joinedload(Usuario.perfil_obj)
    ).filter(Usuario.id == int(user_id)).first()

    if not user or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo"
        )

    # Cria novos tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        user=build_usuario_response(user)
    )


@router.get("/me", response_model=UsuarioResponse)
async def get_me(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retorna dados do usuário autenticado
    """
    # Recarrega com perfil
    user = db.query(Usuario).options(
        joinedload(Usuario.perfil_obj)
    ).filter(Usuario.id == current_user.id).first()
    return build_usuario_response(user)


@router.post("/logout")
async def logout(current_user: Usuario = Depends(get_current_user)):
    """
    Realiza logout do usuário (invalida o token no cliente)
    """
    # Em uma implementação completa, adicionaríamos o token a uma blacklist no Redis
    return {"message": "Logout realizado com sucesso"}


@router.post("/seed")
async def seed_database(db: Session = Depends(get_db)):
    """
    Popula o banco de dados com dados iniciais (executar apenas uma vez)
    """
    import bcrypt
    from app.models.perfil import Perfil

    try:
        # Verifica se já existe admin
        existing_admin = db.query(Usuario).filter(Usuario.email == "ivis_ribeiro@hotmail.com").first()
        if existing_admin:
            return {"message": "Banco já foi populado", "admin_exists": True}

        # Verifica/cria o perfil admin
        admin_perfil = db.query(Perfil).filter(Perfil.codigo == "admin").first()
        if not admin_perfil:
            admin_perfil = Perfil(
                codigo="admin",
                nome="Administrador",
                descricao="Acesso total ao sistema",
                cor="#f5222d",
                is_system=True,
                ativo=True
            )
            db.add(admin_perfil)
            db.commit()
            db.refresh(admin_perfil)

        # Hash da senha usando bcrypt diretamente
        senha = b"admin@123"
        senha_hash = bcrypt.hashpw(senha, bcrypt.gensalt()).decode('utf-8')

        # Cria usuário admin (sem unidade)
        admin = Usuario(
            nome="Ivis Ribeiro",
            email="ivis_ribeiro@hotmail.com",
            senha_hash=senha_hash,
            perfil_id=admin_perfil.id,
            ativo=True
        )
        db.add(admin)
        db.commit()

        return {
            "message": "Admin criado com sucesso!",
            "usuario": "ivis_ribeiro@hotmail.com"
        }
    except Exception as e:
        db.rollback()
        import traceback
        return {"error": str(e), "type": str(type(e).__name__), "trace": traceback.format_exc()}

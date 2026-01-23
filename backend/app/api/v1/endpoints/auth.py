from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
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
from app.schemas.usuario import Token, TokenRefresh, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Realiza login do usuário e retorna tokens JWT
    """
    # Busca usuário pelo email
    user = db.query(Usuario).filter(Usuario.email == form_data.username).first()

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
        user=UsuarioResponse.model_validate(user)
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
    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()

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
        user=UsuarioResponse.model_validate(user)
    )


@router.get("/me", response_model=UsuarioResponse)
async def get_me(current_user: Usuario = Depends(get_current_user)):
    """
    Retorna dados do usuário autenticado
    """
    return UsuarioResponse.model_validate(current_user)


@router.post("/logout")
async def logout(current_user: Usuario = Depends(get_current_user)):
    """
    Realiza logout do usuário (invalida o token no cliente)
    """
    # Em uma implementação completa, adicionaríamos o token a uma blacklist no Redis
    return {"message": "Logout realizado com sucesso"}

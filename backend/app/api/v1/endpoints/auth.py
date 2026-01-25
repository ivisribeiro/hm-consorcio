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


@router.post("/seed")
async def seed_database(db: Session = Depends(get_db)):
    """
    Popula o banco de dados com dados iniciais (executar apenas uma vez)
    """
    from app.core.security import get_password_hash
    from app.models.unidade import Unidade
    from app.models.empresa import Empresa
    from app.models.usuario import PerfilUsuario

    # Verifica se já existe admin
    existing_admin = db.query(Usuario).filter(Usuario.email == "admin@crmconsorcio.com.br").first()
    if existing_admin:
        return {"message": "Banco já foi populado", "admin_exists": True}

    # Cria unidade matriz
    matriz = Unidade(
        nome="Matriz",
        codigo="MTZ001",
        endereco="Av. Principal, 1000",
        cidade="São Paulo",
        estado="SP",
        cep="01310-100",
        telefone="(11) 3000-0000",
        email="matriz@hmcapital.com.br",
        ativo=True
    )
    db.add(matriz)
    db.flush()

    # Cria empresa
    empresa = Empresa(
        razao_social="HM Capital Soluções Financeiras Ltda",
        nome_fantasia="HM Capital",
        cnpj="12.345.678/0001-90",
        endereco="Av. Principal, 1000",
        cidade="São Paulo",
        estado="SP",
        cep="01310-100",
        telefone="(11) 3000-0000",
        email="contato@hmcapital.com.br",
        ativo=True
    )
    db.add(empresa)

    # Cria usuário admin
    admin = Usuario(
        nome="Administrador",
        email="admin@crmconsorcio.com.br",
        senha_hash=get_password_hash("admin123"),
        perfil=PerfilUsuario.ADMIN,
        unidade_id=matriz.id,
        ativo=True
    )
    db.add(admin)

    db.commit()

    return {
        "message": "Banco populado com sucesso!",
        "usuario": "admin@crmconsorcio.com.br",
        "senha": "admin123"
    }

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.models.configuracao import Configuracao
from app.schemas.configuracao import (
    ConfiguracaoCreate, ConfiguracaoUpdate, ConfiguracaoResponse,
    EmpresaSettings, PDFSettings, SistemaSettings
)

router = APIRouter(prefix="/configuracoes", tags=["Configuracoes"])


def get_or_create_config(db: Session, chave: str, categoria: str, valor_default: str = None):
    """Busca ou cria uma configuração"""
    config = db.query(Configuracao).filter(Configuracao.chave == chave).first()
    if not config:
        config = Configuracao(
            chave=chave,
            valor=valor_default,
            categoria=categoria
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


@router.get("/", response_model=List[ConfiguracaoResponse])
async def list_configuracoes(
    categoria: str = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista todas as configurações"""
    query = db.query(Configuracao).filter(Configuracao.ativo == True)
    if categoria:
        query = query.filter(Configuracao.categoria == categoria)
    return query.order_by(Configuracao.categoria, Configuracao.chave).all()


@router.get("/empresa", response_model=EmpresaSettings)
async def get_empresa_settings(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna configurações da empresa"""
    configs = db.query(Configuracao).filter(
        Configuracao.categoria == "empresa",
        Configuracao.ativo == True
    ).all()

    settings = {}
    for c in configs:
        key = c.chave.replace("empresa_", "")
        settings[key] = c.valor

    return EmpresaSettings(**settings)


@router.put("/empresa", response_model=EmpresaSettings)
async def update_empresa_settings(
    settings: EmpresaSettings,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza configurações da empresa"""
    for key, value in settings.model_dump().items():
        chave = f"empresa_{key}"
        config = db.query(Configuracao).filter(Configuracao.chave == chave).first()
        if config:
            config.valor = str(value) if value is not None else None
        else:
            config = Configuracao(
                chave=chave,
                valor=str(value) if value is not None else None,
                categoria="empresa"
            )
            db.add(config)

    db.commit()
    return settings


@router.get("/pdf", response_model=PDFSettings)
async def get_pdf_settings(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna configurações de PDF"""
    configs = db.query(Configuracao).filter(
        Configuracao.categoria == "pdf",
        Configuracao.ativo == True
    ).all()

    settings = {}
    for c in configs:
        key = c.chave.replace("pdf_", "")
        if c.valor in ['True', 'true', '1']:
            settings[key] = True
        elif c.valor in ['False', 'false', '0']:
            settings[key] = False
        else:
            settings[key] = c.valor

    return PDFSettings(**settings) if settings else PDFSettings()


@router.put("/pdf", response_model=PDFSettings)
async def update_pdf_settings(
    settings: PDFSettings,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza configurações de PDF"""
    for key, value in settings.model_dump().items():
        chave = f"pdf_{key}"
        config = db.query(Configuracao).filter(Configuracao.chave == chave).first()
        if config:
            config.valor = str(value) if value is not None else None
        else:
            config = Configuracao(
                chave=chave,
                valor=str(value) if value is not None else None,
                categoria="pdf"
            )
            db.add(config)

    db.commit()
    return settings


@router.get("/sistema", response_model=SistemaSettings)
async def get_sistema_settings(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna configurações do sistema"""
    configs = db.query(Configuracao).filter(
        Configuracao.categoria == "sistema",
        Configuracao.ativo == True
    ).all()

    settings = {}
    for c in configs:
        key = c.chave.replace("sistema_", "")
        if c.valor is None:
            continue
        if c.valor in ['True', 'true', '1']:
            settings[key] = True
        elif c.valor in ['False', 'false', '0']:
            settings[key] = False
        elif c.valor.isdigit():
            settings[key] = int(c.valor)
        else:
            settings[key] = c.valor

    return SistemaSettings(**settings) if settings else SistemaSettings()


@router.put("/sistema", response_model=SistemaSettings)
async def update_sistema_settings(
    settings: SistemaSettings,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza configurações do sistema"""
    for key, value in settings.model_dump().items():
        chave = f"sistema_{key}"
        config = db.query(Configuracao).filter(Configuracao.chave == chave).first()
        if config:
            config.valor = str(value) if value is not None else None
        else:
            config = Configuracao(
                chave=chave,
                valor=str(value) if value is not None else None,
                categoria="sistema"
            )
            db.add(config)

    db.commit()
    return settings


@router.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_configuracoes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Insere configurações padrão (apenas se não existirem)"""
    defaults = [
        # Empresa
        ("empresa_nome", "HM Capital", "empresa", "Nome fantasia da empresa"),
        ("empresa_razao_social", "HM CAPITAL SOLUCOES FINANCEIRAS LTDA", "empresa", "Razão social"),
        ("empresa_cnpj", "00.000.000/0001-00", "empresa", "CNPJ da empresa"),
        ("empresa_endereco", "", "empresa", "Endereço"),
        ("empresa_cidade", "São Paulo", "empresa", "Cidade"),
        ("empresa_estado", "SP", "empresa", "Estado"),
        ("empresa_telefone", "", "empresa", "Telefone"),
        ("empresa_email", "", "empresa", "Email"),

        # PDF
        ("pdf_cor_header", "#2E7D32", "pdf", "Cor do cabeçalho do PDF"),
        ("pdf_cor_section", "#E8F5E9", "pdf", "Cor das seções do PDF"),
        ("pdf_show_logo", "true", "pdf", "Exibir logo no PDF"),
        ("pdf_footer_text", "HM Capital - CRM Consórcios", "pdf", "Texto do rodapé"),

        # Sistema
        ("sistema_items_per_page", "20", "sistema", "Itens por página"),
        ("sistema_session_timeout_minutes", "30", "sistema", "Timeout da sessão em minutos"),
        ("sistema_enable_notifications", "true", "sistema", "Habilitar notificações"),
        ("sistema_default_currency", "BRL", "sistema", "Moeda padrão"),
    ]

    created = 0
    for chave, valor, categoria, descricao in defaults:
        existing = db.query(Configuracao).filter(Configuracao.chave == chave).first()
        if not existing:
            config = Configuracao(
                chave=chave,
                valor=valor,
                categoria=categoria,
                descricao=descricao
            )
            db.add(config)
            created += 1

    db.commit()

    return {"message": f"{created} configurações criadas"}

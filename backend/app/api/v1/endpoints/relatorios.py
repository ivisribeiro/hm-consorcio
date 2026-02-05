from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.beneficio import Beneficio
from app.models.tabela_credito import TabelaCredito
from app.models.empresa import Empresa
from app.models.representante import Representante
from app.models.beneficio_faixa import BeneficioFaixa
from app.services.pdf_generator import ClientePDFGenerator
from app.services.termo_adesao_pdf_generator import TermoAdesaoPDFGenerator
from app.services.ficha_cliente_pdf import FichaClientePDFGenerator
from app.services.contrato_venda_pdf import ContratoVendaPDFGenerator

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


@router.get("/cliente/{cliente_id}/pdf")
async def gerar_pdf_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Gera PDF com dados do cliente (Planejamento Financeiro)
    """
    # Busca cliente
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Busca tabelas de crédito para simulação (baseado nas preferências do cliente)
    tabelas = []
    if cliente.valor_carta_desejado or cliente.parcela_maxima:
        query = db.query(TabelaCredito).filter(TabelaCredito.ativo == True)

        if cliente.parcela_maxima:
            query = query.filter(TabelaCredito.parcela <= cliente.parcela_maxima)

        tabelas = query.order_by(TabelaCredito.valor_credito).limit(4).all()
    else:
        # Se não tem preferências, pega 4 tabelas variadas
        tabelas = db.query(TabelaCredito).filter(
            TabelaCredito.ativo == True
        ).order_by(TabelaCredito.valor_credito).limit(4).all()

    # Gera PDF
    pdf_generator = ClientePDFGenerator(
        cliente=cliente,
        tabelas_simulacao=tabelas
    )

    pdf_bytes = pdf_generator.generate()

    # Retorna como streaming response
    filename = f"planejamento_{cliente.nome.replace(' ', '_')}_{cliente_id}.pdf"

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/beneficio/{beneficio_id}/pdf")
async def gerar_pdf_beneficio(
    beneficio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Gera PDF com dados do benefício e cliente
    """
    # Busca benefício
    beneficio = db.query(Beneficio).filter(Beneficio.id == beneficio_id).first()
    if not beneficio:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")

    # Busca cliente
    cliente = db.query(Cliente).filter(Cliente.id == beneficio.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Busca tabela de crédito do benefício
    tabela = db.query(TabelaCredito).filter(TabelaCredito.id == beneficio.tabela_credito_id).first()
    tabelas = [tabela] if tabela else []

    # Gera PDF
    pdf_generator = ClientePDFGenerator(
        cliente=cliente,
        beneficio=beneficio,
        tabelas_simulacao=tabelas
    )

    pdf_bytes = pdf_generator.generate()

    # Retorna como streaming response
    filename = f"proposta_{beneficio_id}_{cliente.nome.replace(' ', '_')}.pdf"

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/ficha-atendimento/{cliente_id}/pdf")
async def gerar_ficha_atendimento_pdf(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Gera PDF da Ficha de Atendimento do Cliente (3 páginas)
    - Página 1: Capa profissional
    - Página 2: Cadastro Pessoa Física
    - Página 3: Proposta de Orçamento
    """
    # Busca cliente
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Busca representante do cliente
    representante = None
    if cliente.representante_id:
        representante = db.query(Usuario).filter(Usuario.id == cliente.representante_id).first()
    if not representante:
        representante = current_user

    # Gera PDF
    pdf_generator = FichaClientePDFGenerator(
        cliente=cliente,
        representante=representante
    )

    pdf_bytes = pdf_generator.generate()
    filename = pdf_generator.get_filename()

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/termo-adesao/{beneficio_id}/pdf")
async def gerar_termo_adesao_pdf(
    beneficio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Gera PDF do termo de adesão ao consórcio
    """
    # Busca benefício
    beneficio = db.query(Beneficio).filter(Beneficio.id == beneficio_id).first()
    if not beneficio:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")

    # Busca cliente
    cliente = db.query(Cliente).filter(Cliente.id == beneficio.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Busca usuário (representante do benefício ou usuário logado)
    usuario = None
    if beneficio.representante_id:
        usuario = db.query(Usuario).filter(Usuario.id == beneficio.representante_id).first()
    if not usuario:
        usuario = current_user

    # Busca empresa (diretamente do benefício)
    empresa = None
    if beneficio.empresa_id:
        empresa = db.query(Empresa).filter(Empresa.id == beneficio.empresa_id).first()

    # Busca representante (modelo Representante com razão social)
    representante = None
    if beneficio.unidade_id:
        representante = db.query(Representante).filter(
            Representante.unidade_id == beneficio.unidade_id,
            Representante.ativo == True
        ).first()
    if not representante:
        representante = db.query(Representante).filter(Representante.ativo == True).first()

    # Busca faixas de parcelas do benefício
    faixas = db.query(BeneficioFaixa).filter(
        BeneficioFaixa.beneficio_id == beneficio_id
    ).order_by(BeneficioFaixa.parcela_inicio).all()

    # Gera PDF do termo de adesão
    pdf_generator = TermoAdesaoPDFGenerator(
        cliente=cliente,
        beneficio=beneficio,
        usuario=usuario,
        empresa=empresa,
        representante=representante,
        faixas=faixas
    )

    pdf_bytes = pdf_generator.generate()

    # Retorna como streaming response
    filename = f"termo_adesao_{beneficio_id}_{cliente.nome.replace(' ', '_')}.pdf"

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/contrato/{beneficio_id}/pdf")
async def gerar_contrato_venda_pdf(
    beneficio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Gera PDF do Contrato de Venda (10 páginas)
    - Página 1: Contrato Principal + Dados do Cliente
    - Página 2: Definições e Obrigações
    - Página 3: Obrigações e Condições
    - Página 4: Disposições Gerais
    - Página 5: Declarações e PEP
    - Página 6: Declaração de Ciência
    - Página 7: Termo de Consultoria (versão 1)
    - Página 8: Termo de Consultoria (versão 2)
    - Página 9: Questionário de Checagem
    - Página 10: Ciência da Análise Creditícia
    """
    # Busca benefício
    beneficio = db.query(Beneficio).filter(Beneficio.id == beneficio_id).first()
    if not beneficio:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")

    # Busca cliente
    cliente = db.query(Cliente).filter(Cliente.id == beneficio.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Busca representante (do benefício)
    representante = None
    if beneficio.representante_id:
        representante = db.query(Representante).filter(Representante.id == beneficio.representante_id).first()

    # Busca empresa (do benefício)
    empresa = None
    if beneficio.empresa_id:
        empresa = db.query(Empresa).filter(Empresa.id == beneficio.empresa_id).first()

    # Gera PDF do contrato
    pdf_generator = ContratoVendaPDFGenerator(
        cliente=cliente,
        beneficio=beneficio,
        representante=representante,
        empresa=empresa
    )

    pdf_bytes = pdf_generator.generate()
    filename = pdf_generator.get_filename()

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

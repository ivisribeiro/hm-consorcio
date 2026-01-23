from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from io import BytesIO

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.models.beneficio import Beneficio
from app.models.cliente import Cliente
from app.models.contrato import Contrato
from app.schemas.contrato import (
    ContratoCreate, ContratoUpdate, ContratoResponse,
    ContratoListResponse, ContratoStatusUpdate, ContratoAssinaturaUpdate,
    BeneficioSimples, ClienteSimples
)
from app.services.contrato_pdf_generator import ContratoPDFGenerator

router = APIRouter(prefix="/contratos", tags=["Contratos"])


@router.get("/", response_model=List[ContratoListResponse])
async def list_contratos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista contratos com filtros"""
    query = db.query(Contrato).filter(Contrato.ativo == True)

    if status:
        query = query.filter(Contrato.status == status)

    contratos = query.order_by(Contrato.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for c in contratos:
        beneficio = db.query(Beneficio).filter(Beneficio.id == c.beneficio_id).first()
        cliente = None
        if beneficio:
            cliente = db.query(Cliente).filter(Cliente.id == beneficio.cliente_id).first()

        # Aplicar filtro de busca se fornecido
        if search:
            search_lower = search.lower()
            match = False
            if cliente and cliente.nome and search_lower in cliente.nome.lower():
                match = True
            if cliente and cliente.cpf and search_lower in cliente.cpf:
                match = True
            if c.numero and search_lower in c.numero.lower():
                match = True
            if not match:
                continue

        result.append(ContratoListResponse(
            id=c.id,
            numero=c.numero,
            beneficio_id=c.beneficio_id,
            cliente_nome=cliente.nome if cliente else None,
            cliente_cpf=cliente.cpf if cliente else None,
            valor_credito=c.valor_credito,
            status=c.status,
            data_geracao=c.data_geracao,
            data_assinatura=c.data_assinatura
        ))

    return result


@router.post("/", response_model=ContratoResponse, status_code=status.HTTP_201_CREATED)
async def create_contrato(
    contrato_data: ContratoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria contrato a partir de um benefício"""
    beneficio = db.query(Beneficio).filter(Beneficio.id == contrato_data.beneficio_id).first()
    if not beneficio:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")

    # Verificar se já existe contrato para este benefício
    existing = db.query(Contrato).filter(
        Contrato.beneficio_id == beneficio.id,
        Contrato.ativo == True
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Já existe um contrato para este benefício")

    # Gerar número do contrato (ANO + sequencial)
    year = datetime.now().year
    last_contrato = db.query(Contrato).order_by(Contrato.id.desc()).first()
    next_id = (last_contrato.id + 1) if last_contrato else 1
    numero = f"{year}{str(next_id).zfill(6)}"

    contrato = Contrato(
        numero=numero,
        beneficio_id=beneficio.id,
        valor_credito=beneficio.valor_credito,
        parcela=beneficio.parcela,
        prazo=beneficio.prazo_grupo,
        taxa_administracao=beneficio.taxa_administracao,
        fundo_reserva=beneficio.fundo_reserva,
        observacoes=contrato_data.observacoes,
        status="gerado"
    )

    db.add(contrato)

    # Atualizar status do benefício
    beneficio.data_contrato = datetime.utcnow()

    db.commit()
    db.refresh(contrato)

    # Carregar dados relacionados
    cliente = db.query(Cliente).filter(Cliente.id == beneficio.cliente_id).first()

    response = ContratoResponse(
        id=contrato.id,
        numero=contrato.numero,
        beneficio_id=contrato.beneficio_id,
        status=contrato.status,
        valor_credito=contrato.valor_credito,
        parcela=contrato.parcela,
        prazo=contrato.prazo,
        taxa_administracao=contrato.taxa_administracao,
        fundo_reserva=contrato.fundo_reserva,
        data_geracao=contrato.data_geracao,
        data_envio=contrato.data_envio,
        data_assinatura=contrato.data_assinatura,
        data_registro=contrato.data_registro,
        data_cancelamento=contrato.data_cancelamento,
        assinado_cliente=contrato.assinado_cliente,
        assinado_representante=contrato.assinado_representante,
        assinado_testemunha1=contrato.assinado_testemunha1,
        assinado_testemunha2=contrato.assinado_testemunha2,
        pdf_path=contrato.pdf_path,
        observacoes=contrato.observacoes,
        motivo_cancelamento=contrato.motivo_cancelamento,
        ativo=contrato.ativo,
        created_at=contrato.created_at,
        updated_at=contrato.updated_at,
        beneficio=BeneficioSimples(
            id=beneficio.id,
            tipo_bem=beneficio.tipo_bem,
            valor_credito=beneficio.valor_credito,
            grupo=beneficio.grupo,
            cota=beneficio.cota
        ) if beneficio else None,
        cliente=ClienteSimples(
            id=cliente.id,
            nome=cliente.nome,
            cpf=cliente.cpf,
            telefone=cliente.telefone,
            email=cliente.email
        ) if cliente else None
    )

    return response


@router.get("/{contrato_id}", response_model=ContratoResponse)
async def get_contrato(
    contrato_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém um contrato pelo ID"""
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    beneficio = db.query(Beneficio).filter(Beneficio.id == contrato.beneficio_id).first()
    cliente = None
    if beneficio:
        cliente = db.query(Cliente).filter(Cliente.id == beneficio.cliente_id).first()

    response = ContratoResponse(
        id=contrato.id,
        numero=contrato.numero,
        beneficio_id=contrato.beneficio_id,
        status=contrato.status,
        valor_credito=contrato.valor_credito,
        parcela=contrato.parcela,
        prazo=contrato.prazo,
        taxa_administracao=contrato.taxa_administracao,
        fundo_reserva=contrato.fundo_reserva,
        data_geracao=contrato.data_geracao,
        data_envio=contrato.data_envio,
        data_assinatura=contrato.data_assinatura,
        data_registro=contrato.data_registro,
        data_cancelamento=contrato.data_cancelamento,
        assinado_cliente=contrato.assinado_cliente,
        assinado_representante=contrato.assinado_representante,
        assinado_testemunha1=contrato.assinado_testemunha1,
        assinado_testemunha2=contrato.assinado_testemunha2,
        pdf_path=contrato.pdf_path,
        observacoes=contrato.observacoes,
        motivo_cancelamento=contrato.motivo_cancelamento,
        ativo=contrato.ativo,
        created_at=contrato.created_at,
        updated_at=contrato.updated_at,
        beneficio=BeneficioSimples(
            id=beneficio.id,
            tipo_bem=beneficio.tipo_bem,
            valor_credito=beneficio.valor_credito,
            grupo=beneficio.grupo,
            cota=beneficio.cota
        ) if beneficio else None,
        cliente=ClienteSimples(
            id=cliente.id,
            nome=cliente.nome,
            cpf=cliente.cpf,
            telefone=cliente.telefone,
            email=cliente.email
        ) if cliente else None
    )

    return response


@router.put("/{contrato_id}", response_model=ContratoResponse)
async def update_contrato(
    contrato_id: int,
    contrato_data: ContratoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza um contrato"""
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    update_data = contrato_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contrato, key, value)

    db.commit()
    db.refresh(contrato)

    return await get_contrato(contrato_id, db, current_user)


@router.patch("/{contrato_id}/status", response_model=ContratoResponse)
async def update_contrato_status(
    contrato_id: int,
    status_data: ContratoStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza o status do contrato"""
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    # Validar transições de status
    valid_transitions = {
        "gerado": ["enviado_assinatura", "cancelado"],
        "enviado_assinatura": ["assinado", "cancelado"],
        "assinado": ["registrado", "cancelado"],
        "registrado": [],  # Estado final, não pode mudar
        "cancelado": [],  # Estado final
    }

    allowed = valid_transitions.get(contrato.status, [])
    if status_data.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Transição de '{contrato.status}' para '{status_data.status}' não permitida"
        )

    contrato.status = status_data.status
    now = datetime.utcnow()

    if status_data.status == "enviado_assinatura":
        contrato.data_envio = now
    elif status_data.status == "assinado":
        contrato.data_assinatura = now
    elif status_data.status == "registrado":
        contrato.data_registro = now
    elif status_data.status == "cancelado":
        contrato.data_cancelamento = now
        contrato.motivo_cancelamento = status_data.motivo_cancelamento

    db.commit()
    db.refresh(contrato)

    return await get_contrato(contrato_id, db, current_user)


@router.patch("/{contrato_id}/assinaturas", response_model=ContratoResponse)
async def update_contrato_assinaturas(
    contrato_id: int,
    assinatura_data: ContratoAssinaturaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Registra assinaturas no contrato"""
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    update_data = assinatura_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contrato, key, value)

    # Auto-atualizar status se todas as assinaturas forem coletadas
    if (contrato.assinado_cliente and contrato.assinado_representante and
        contrato.assinado_testemunha1 and contrato.assinado_testemunha2):
        if contrato.status == "enviado_assinatura":
            contrato.status = "assinado"
            contrato.data_assinatura = datetime.utcnow()

    db.commit()
    db.refresh(contrato)

    return await get_contrato(contrato_id, db, current_user)


@router.delete("/{contrato_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contrato(
    contrato_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Desativa um contrato (soft delete)"""
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    if contrato.status in ["assinado", "registrado"]:
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir um contrato assinado ou registrado"
        )

    contrato.ativo = False
    contrato.status = "cancelado"
    contrato.data_cancelamento = datetime.utcnow()
    db.commit()

    return None


@router.get("/{contrato_id}/pdf")
async def download_contrato_pdf(
    contrato_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Gera e retorna PDF do contrato"""
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    beneficio = db.query(Beneficio).filter(Beneficio.id == contrato.beneficio_id).first()
    if not beneficio:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")

    cliente = db.query(Cliente).filter(Cliente.id == beneficio.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Buscar representante e empresa se existirem
    representante = None
    if beneficio.representante_id:
        representante = db.query(Usuario).filter(Usuario.id == beneficio.representante_id).first()

    empresa = None
    if beneficio.empresa_id:
        from app.models.empresa import Empresa
        empresa = db.query(Empresa).filter(Empresa.id == beneficio.empresa_id).first()

    generator = ContratoPDFGenerator(cliente, beneficio, representante, empresa)
    pdf_bytes = generator.generate()

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=contrato_{contrato.numero}.pdf"}
    )

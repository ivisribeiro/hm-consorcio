from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Literal
from datetime import datetime
from decimal import Decimal
import csv
import io

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.beneficio import Beneficio
from app.models.beneficio_historico import BeneficioHistorico
from app.models.beneficio_faixa import BeneficioFaixa
from app.models.tabela_credito import TabelaCredito
from app.schemas.beneficio import (
    BeneficioCreate, BeneficioUpdate, BeneficioResponse,
    BeneficioListResponse, BeneficioStatusUpdate,
    TabelaCreditoCreate, TabelaCreditoUpdate, TabelaCreditoResponse,
    TabelaCreditoImportResult,
    AdministradoraCreate, AdministradoraUpdate, AdministradoraResponse,
    SimulacaoRequest, SimulacaoResponse,
    BeneficioHistoricoResponse,
    BeneficioFaixaCreate, BeneficioFaixaUpdate, BeneficioFaixaResponse
)
from app.models.administradora import Administradora

# Status and type definitions (using strings since model uses String columns)
StatusBeneficio = Literal[
    "rascunho", "proposto", "aceito", "rejeitado",
    "contrato_gerado", "contrato_assinado", "aguardando_cadastro",
    "cadastrado", "termo_gerado", "ativo", "cancelado"
]
TipoBem = Literal["imovel", "carro", "moto"]

router = APIRouter(prefix="/beneficios", tags=["Benefícios"])


# ==================== BENEFÍCIOS ====================

@router.get("/", response_model=List[BeneficioListResponse])
async def list_beneficios(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    cliente_id: Optional[int] = None,
    status: Optional[StatusBeneficio] = None,
    tipo_bem: Optional[TipoBem] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista benefícios com filtros"""
    query = db.query(Beneficio).filter(Beneficio.ativo == True)

    if cliente_id:
        query = query.filter(Beneficio.cliente_id == cliente_id)
    if status:
        query = query.filter(Beneficio.status == status)
    if tipo_bem:
        query = query.filter(Beneficio.tipo_bem == tipo_bem)

    beneficios = query.order_by(Beneficio.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for b in beneficios:
        cliente = db.query(Cliente).filter(Cliente.id == b.cliente_id).first()
        result.append(BeneficioListResponse(
            id=b.id,
            cliente_id=b.cliente_id,
            cliente_nome=cliente.nome if cliente else None,
            tipo_bem=b.tipo_bem,
            valor_credito=b.valor_credito,
            parcela=b.parcela,
            prazo_grupo=b.prazo_grupo,
            status=b.status,
            grupo=b.grupo,
            cota=b.cota,
            created_at=b.created_at
        ))

    return result


@router.post("/", response_model=BeneficioResponse, status_code=status.HTTP_201_CREATED)
async def create_beneficio(
    beneficio_data: BeneficioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria um novo benefício baseado na tabela de crédito"""
    # Verifica se cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == beneficio_data.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Verifica tabela de crédito
    tabela = db.query(TabelaCredito).filter(TabelaCredito.id == beneficio_data.tabela_credito_id).first()
    if not tabela:
        raise HTTPException(status_code=404, detail="Tabela de crédito não encontrada")

    # Validação de capacidade de pagamento (parcela não pode exceder 30% do salário)
    if cliente.salario:
        limite_parcela = float(cliente.salario) * 0.30
        if float(tabela.parcela) > limite_parcela:
            raise HTTPException(
                status_code=400,
                detail=f"Parcela de R$ {tabela.parcela} excede 30% do salário (R$ {limite_parcela:.2f})"
            )

    # Cria benefício com dados da tabela (administradora vem da tabela de crédito)
    beneficio = Beneficio(
        cliente_id=beneficio_data.cliente_id,
        representante_id=beneficio_data.representante_id or current_user.id,
        consultor_id=beneficio_data.consultor_id,
        unidade_id=beneficio_data.unidade_id,
        empresa_id=beneficio_data.empresa_id,
        tabela_credito_id=beneficio_data.tabela_credito_id,
        administradora_id=tabela.administradora_id,  # Auto-preenche da tabela de crédito
        tipo_bem=tabela.tipo_bem,
        prazo_grupo=tabela.prazo,
        valor_credito=tabela.valor_credito,
        parcela=tabela.parcela,
        fundo_reserva=tabela.fundo_reserva,
        taxa_administracao=tabela.taxa_administracao,
        seguro_prestamista=tabela.seguro_prestamista,
        indice_correcao=tabela.indice_correcao,
        qtd_participantes=tabela.qtd_participantes,
        tipo_plano=tabela.tipo_plano,
        observacoes=beneficio_data.observacoes,
        status="rascunho"
    )

    db.add(beneficio)
    db.commit()
    db.refresh(beneficio)

    return beneficio


@router.get("/{beneficio_id}", response_model=BeneficioResponse)
async def get_beneficio(
    beneficio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém um benefício pelo ID"""
    beneficio = db.query(Beneficio).filter(Beneficio.id == beneficio_id).first()

    if not beneficio:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")

    return beneficio


@router.put("/{beneficio_id}", response_model=BeneficioResponse)
async def update_beneficio(
    beneficio_id: int,
    beneficio_data: BeneficioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza um benefício"""
    beneficio = db.query(Beneficio).filter(Beneficio.id == beneficio_id).first()

    if not beneficio:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")

    update_data = beneficio_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(beneficio, key, value)

    db.commit()
    db.refresh(beneficio)

    return beneficio


@router.patch("/{beneficio_id}/status", response_model=BeneficioResponse)
async def update_beneficio_status(
    beneficio_id: int,
    status_data: BeneficioStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza o status de um benefício seguindo o workflow (avançar ou voltar)"""
    beneficio = db.query(Beneficio).filter(Beneficio.id == beneficio_id).first()

    if not beneficio:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")

    status_anterior = beneficio.status

    # Define o fluxo principal (ordem)
    status_flow = [
        "rascunho", "proposto", "aceito", "contrato_gerado", "contrato_assinado",
        "aguardando_cadastro", "cadastrado", "termo_gerado", "ativo"
    ]

    # Valida transições de status (avançar ou voltar no fluxo)
    valid_forward = {
        "rascunho": ["proposto", "cancelado"],
        "proposto": ["aceito", "rejeitado"],
        "aceito": ["contrato_gerado", "cancelado"],
        "contrato_gerado": ["contrato_assinado", "cancelado"],
        "contrato_assinado": ["aguardando_cadastro", "cancelado"],
        "aguardando_cadastro": ["cadastrado", "cancelado"],
        "cadastrado": ["termo_gerado", "cancelado"],
        "termo_gerado": ["ativo", "cancelado"],
    }

    # Transições para voltar (status anterior no fluxo)
    valid_backward = {
        "proposto": ["rascunho"],
        "aceito": ["proposto"],
        "contrato_gerado": ["aceito"],
        "contrato_assinado": ["contrato_gerado"],
        "aguardando_cadastro": ["contrato_assinado"],
        "cadastrado": ["aguardando_cadastro"],
        "termo_gerado": ["cadastrado"],
    }

    # Verifica se é uma transição válida (avançar ou voltar)
    forward_allowed = valid_forward.get(beneficio.status, [])
    backward_allowed = valid_backward.get(beneficio.status, [])

    is_forward = status_data.status in forward_allowed
    is_backward = status_data.status in backward_allowed

    if not is_forward and not is_backward:
        raise HTTPException(
            status_code=400,
            detail=f"Transição de {beneficio.status} para {status_data.status} não permitida"
        )

    # Determina a ação para o histórico
    if status_data.status == "cancelado":
        acao = "cancelou"
    elif status_data.status == "rejeitado":
        acao = "rejeitou"
    elif is_backward:
        acao = "voltou"
    else:
        acao = "avancou"

    # Atualiza status e datas correspondentes
    beneficio.status = status_data.status
    now = datetime.utcnow()

    if status_data.status == "proposto":
        beneficio.data_proposta = now
    elif status_data.status == "aceito":
        beneficio.data_aceite = now
    elif status_data.status == "rejeitado":
        beneficio.data_rejeicao = now
        beneficio.motivo_rejeicao = status_data.motivo_rejeicao
    elif status_data.status == "contrato_gerado":
        beneficio.data_contrato = now
    elif status_data.status == "contrato_assinado":
        beneficio.data_assinatura_contrato = now
    elif status_data.status == "aguardando_cadastro":
        pass  # Apenas mudança de status
    elif status_data.status == "cadastrado":
        beneficio.data_cadastro_administradora = now
    elif status_data.status == "termo_gerado":
        beneficio.data_termo = now
    elif status_data.status == "ativo":
        beneficio.data_ativacao = now
        beneficio.data_assinatura_termo = now
    elif status_data.status == "cancelado":
        beneficio.data_cancelamento = now
        beneficio.motivo_cancelamento = status_data.motivo_cancelamento

    # Registra histórico
    observacao = None
    if status_data.status == "rejeitado" and status_data.motivo_rejeicao:
        observacao = status_data.motivo_rejeicao
    elif status_data.status == "cancelado" and status_data.motivo_cancelamento:
        observacao = status_data.motivo_cancelamento

    historico = BeneficioHistorico(
        beneficio_id=beneficio.id,
        usuario_id=current_user.id,
        status_anterior=status_anterior,
        status_novo=status_data.status,
        acao=acao,
        observacao=observacao
    )
    db.add(historico)

    db.commit()
    db.refresh(beneficio)

    return beneficio


@router.get("/{beneficio_id}/historico", response_model=List[BeneficioHistoricoResponse])
async def get_beneficio_historico(
    beneficio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém o histórico de mudanças de status de um benefício"""
    beneficio = db.query(Beneficio).filter(Beneficio.id == beneficio_id).first()

    if not beneficio:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")

    historicos = db.query(BeneficioHistorico).options(
        joinedload(BeneficioHistorico.usuario)
    ).filter(
        BeneficioHistorico.beneficio_id == beneficio_id
    ).order_by(BeneficioHistorico.created_at.desc()).all()

    result = []
    for h in historicos:
        result.append(BeneficioHistoricoResponse(
            id=h.id,
            beneficio_id=h.beneficio_id,
            usuario_id=h.usuario_id,
            usuario_nome=h.usuario.nome if h.usuario else None,
            status_anterior=h.status_anterior,
            status_novo=h.status_novo,
            acao=h.acao,
            observacao=h.observacao,
            created_at=h.created_at
        ))

    return result


# ==================== FAIXAS DE PARCELAS ====================

@router.get("/{beneficio_id}/faixas", response_model=List[BeneficioFaixaResponse])
async def list_faixas(
    beneficio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista faixas de parcelas de um benefício"""
    beneficio = db.query(Beneficio).filter(Beneficio.id == beneficio_id).first()
    if not beneficio:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")

    faixas = db.query(BeneficioFaixa).filter(
        BeneficioFaixa.beneficio_id == beneficio_id
    ).order_by(BeneficioFaixa.parcela_inicio).all()

    return faixas


@router.post("/{beneficio_id}/faixas", response_model=BeneficioFaixaResponse, status_code=status.HTTP_201_CREATED)
async def create_faixa(
    beneficio_id: int,
    faixa_data: BeneficioFaixaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria uma faixa de parcela para o benefício"""
    beneficio = db.query(Beneficio).filter(Beneficio.id == beneficio_id).first()
    if not beneficio:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")

    faixa = BeneficioFaixa(
        beneficio_id=beneficio_id,
        **faixa_data.model_dump()
    )
    db.add(faixa)
    db.commit()
    db.refresh(faixa)
    return faixa


@router.put("/{beneficio_id}/faixas/{faixa_id}", response_model=BeneficioFaixaResponse)
async def update_faixa(
    beneficio_id: int,
    faixa_id: int,
    faixa_data: BeneficioFaixaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza uma faixa de parcela"""
    faixa = db.query(BeneficioFaixa).filter(
        BeneficioFaixa.id == faixa_id,
        BeneficioFaixa.beneficio_id == beneficio_id
    ).first()
    if not faixa:
        raise HTTPException(status_code=404, detail="Faixa não encontrada")

    update_data = faixa_data.model_dump()
    for key, value in update_data.items():
        setattr(faixa, key, value)

    db.commit()
    db.refresh(faixa)
    return faixa


@router.delete("/{beneficio_id}/faixas/{faixa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faixa(
    beneficio_id: int,
    faixa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Remove uma faixa de parcela"""
    faixa = db.query(BeneficioFaixa).filter(
        BeneficioFaixa.id == faixa_id,
        BeneficioFaixa.beneficio_id == beneficio_id
    ).first()
    if not faixa:
        raise HTTPException(status_code=404, detail="Faixa não encontrada")

    db.delete(faixa)
    db.commit()


# ==================== TABELAS DE CRÉDITO ====================

@router.get("/tabelas/", response_model=List[TabelaCreditoResponse])
async def list_tabelas_credito(
    tipo_bem: Optional[TipoBem] = None,
    administradora_id: Optional[int] = None,
    ativo: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista tabelas de crédito"""
    query = db.query(TabelaCredito).options(joinedload(TabelaCredito.administradora))

    if tipo_bem:
        query = query.filter(TabelaCredito.tipo_bem == tipo_bem)
    if administradora_id:
        query = query.filter(TabelaCredito.administradora_id == administradora_id)
    if ativo is not None:
        query = query.filter(TabelaCredito.ativo == ativo)

    return query.order_by(TabelaCredito.valor_credito).all()


@router.post("/tabelas/", response_model=TabelaCreditoResponse, status_code=status.HTTP_201_CREATED)
async def create_tabela_credito(
    tabela_data: TabelaCreditoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria uma nova tabela de crédito"""
    # Validar administradora se fornecida
    if tabela_data.administradora_id:
        admin = db.query(Administradora).filter(Administradora.id == tabela_data.administradora_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Administradora não encontrada")

    tabela = TabelaCredito(**tabela_data.model_dump())
    db.add(tabela)
    db.commit()
    db.refresh(tabela)

    # Reload with relationship
    return db.query(TabelaCredito).options(
        joinedload(TabelaCredito.administradora)
    ).filter(TabelaCredito.id == tabela.id).first()


@router.put("/tabelas/{tabela_id}", response_model=TabelaCreditoResponse)
async def update_tabela_credito(
    tabela_id: int,
    tabela_data: TabelaCreditoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza uma tabela de crédito"""
    tabela = db.query(TabelaCredito).filter(TabelaCredito.id == tabela_id).first()

    if not tabela:
        raise HTTPException(status_code=404, detail="Tabela não encontrada")

    # Validar administradora se fornecida
    if tabela_data.administradora_id:
        admin = db.query(Administradora).filter(Administradora.id == tabela_data.administradora_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Administradora não encontrada")

    update_data = tabela_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tabela, key, value)

    db.commit()
    db.refresh(tabela)

    # Reload with relationship
    return db.query(TabelaCredito).options(
        joinedload(TabelaCredito.administradora)
    ).filter(TabelaCredito.id == tabela.id).first()


@router.post("/tabelas/importar-csv", response_model=TabelaCreditoImportResult)
async def importar_tabelas_csv(
    file: UploadFile = File(...),
    administradora_id: Optional[int] = Query(None, description="ID da administradora para todas as tabelas"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Importa tabelas de crédito via CSV.

    Colunas esperadas (separador: vírgula ou ponto-e-vírgula):
    - nome (obrigatório)
    - tipo_bem (obrigatório: imovel, carro, moto)
    - prazo (obrigatório: número de meses)
    - valor_credito (obrigatório)
    - parcela (obrigatório)
    - fundo_reserva (opcional, default: 2.5)
    - taxa_administracao (opcional, default: 26.0)
    - seguro_prestamista (opcional, default: 0)
    - indice_correcao (opcional, default: INCC)
    - qtd_participantes (opcional, default: 4076)
    - tipo_plano (opcional, default: Normal)
    - administradora_id (opcional, sobrescreve o parâmetro da query)
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser CSV")

    # Validar administradora se fornecida via query
    if administradora_id:
        admin = db.query(Administradora).filter(Administradora.id == administradora_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Administradora não encontrada")

    content = await file.read()

    # Tentar decodificar com diferentes encodings
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            text = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise HTTPException(status_code=400, detail="Não foi possível decodificar o arquivo")

    # Detectar separador
    first_line = text.split('\n')[0]
    separator = ';' if ';' in first_line else ','

    reader = csv.DictReader(io.StringIO(text), delimiter=separator)

    # Normalizar nomes das colunas (lowercase, sem espaços)
    if reader.fieldnames:
        reader.fieldnames = [f.strip().lower().replace(' ', '_') for f in reader.fieldnames]

    importados = 0
    erros = []
    total = 0

    tipo_bem_map = {
        'imovel': 'imovel', 'imóvel': 'imovel', 'imoveis': 'imovel', 'imóveis': 'imovel',
        'carro': 'carro', 'carros': 'carro', 'auto': 'carro', 'automovel': 'carro', 'automóvel': 'carro',
        'moto': 'moto', 'motos': 'moto', 'motocicleta': 'moto'
    }

    for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
        total += 1
        try:
            # Normalizar keys
            row = {k.strip().lower().replace(' ', '_'): v.strip() if v else '' for k, v in row.items()}

            # Campos obrigatórios
            nome = row.get('nome', '')
            tipo_bem_raw = row.get('tipo_bem', '').lower()
            prazo_str = row.get('prazo', '')
            valor_credito_str = row.get('valor_credito', '')
            parcela_str = row.get('parcela', '')

            if not nome:
                erros.append(f"Linha {row_num}: nome é obrigatório")
                continue

            tipo_bem = tipo_bem_map.get(tipo_bem_raw)
            if not tipo_bem:
                erros.append(f"Linha {row_num}: tipo_bem inválido '{tipo_bem_raw}' (use: imovel, carro, moto)")
                continue

            # Parse números (aceita vírgula ou ponto como decimal)
            def parse_number(val, default=None):
                if not val:
                    return default
                val = val.replace('.', '').replace(',', '.')  # 1.000,50 -> 1000.50
                # Se terminar com ponto, pode ser separador de milhar errado
                if val.endswith('.'):
                    val = val[:-1]
                return Decimal(val)

            try:
                prazo = int(prazo_str) if prazo_str else None
                if not prazo:
                    erros.append(f"Linha {row_num}: prazo é obrigatório")
                    continue
            except ValueError:
                erros.append(f"Linha {row_num}: prazo inválido '{prazo_str}'")
                continue

            try:
                valor_credito = parse_number(valor_credito_str)
                if not valor_credito:
                    erros.append(f"Linha {row_num}: valor_credito é obrigatório")
                    continue
            except Exception:
                erros.append(f"Linha {row_num}: valor_credito inválido '{valor_credito_str}'")
                continue

            try:
                parcela = parse_number(parcela_str)
                if not parcela:
                    erros.append(f"Linha {row_num}: parcela é obrigatório")
                    continue
            except Exception:
                erros.append(f"Linha {row_num}: parcela inválido '{parcela_str}'")
                continue

            # Campos opcionais
            fundo_reserva = parse_number(row.get('fundo_reserva', ''), Decimal('2.5'))
            taxa_administracao = parse_number(row.get('taxa_administracao', ''), Decimal('26.0'))
            seguro_prestamista = parse_number(row.get('seguro_prestamista', ''), Decimal('0'))
            valor_intermediacao = parse_number(row.get('valor_intermediacao', ''), Decimal('0'))
            indice_correcao = row.get('indice_correcao', 'INCC') or 'INCC'
            qtd_participantes = int(row.get('qtd_participantes', '') or '4076')
            tipo_plano = row.get('tipo_plano', 'Normal') or 'Normal'

            # Administradora: prioridade para o valor da linha, depois parâmetro da query
            admin_id_row = row.get('administradora_id', '')
            if admin_id_row:
                try:
                    admin_id = int(admin_id_row)
                except ValueError:
                    admin_id = administradora_id
            else:
                admin_id = administradora_id

            # Criar tabela
            tabela = TabelaCredito(
                nome=nome,
                tipo_bem=tipo_bem,
                prazo=prazo,
                valor_credito=valor_credito,
                parcela=parcela,
                fundo_reserva=fundo_reserva,
                taxa_administracao=taxa_administracao,
                seguro_prestamista=seguro_prestamista,
                valor_intermediacao=valor_intermediacao,
                indice_correcao=indice_correcao,
                qtd_participantes=qtd_participantes,
                tipo_plano=tipo_plano,
                administradora_id=admin_id,
                ativo=True
            )

            db.add(tabela)
            importados += 1

        except Exception as e:
            erros.append(f"Linha {row_num}: erro inesperado - {str(e)}")

    if importados > 0:
        db.commit()

    return TabelaCreditoImportResult(
        total=total,
        importados=importados,
        erros=erros[:20]  # Limitar a 20 erros para não sobrecarregar
    )


@router.post("/simular", response_model=SimulacaoResponse)
async def simular_beneficio(
    simulacao: SimulacaoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Simula opções de benefício baseado nos critérios"""
    query = db.query(TabelaCredito).filter(
        TabelaCredito.tipo_bem == simulacao.tipo_bem,
        TabelaCredito.ativo == True
    )

    if simulacao.valor_credito_min:
        query = query.filter(TabelaCredito.valor_credito >= simulacao.valor_credito_min)
    if simulacao.valor_credito_max:
        query = query.filter(TabelaCredito.valor_credito <= simulacao.valor_credito_max)
    if simulacao.parcela_max:
        query = query.filter(TabelaCredito.parcela <= simulacao.parcela_max)

    tabelas = query.order_by(TabelaCredito.valor_credito).all()

    return SimulacaoResponse(tabelas=tabelas)


# ==================== ADMINISTRADORAS ====================

@router.get("/administradoras/", response_model=List[AdministradoraResponse])
async def list_administradoras(
    ativo: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista administradoras"""
    query = db.query(Administradora)
    if ativo is not None:
        query = query.filter(Administradora.ativo == ativo)
    return query.all()


@router.post("/administradoras/", response_model=AdministradoraResponse, status_code=status.HTTP_201_CREATED)
async def create_administradora(
    admin_data: AdministradoraCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria uma nova administradora"""
    admin = Administradora(**admin_data.model_dump())
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@router.put("/administradoras/{admin_id}", response_model=AdministradoraResponse)
async def update_administradora(
    admin_id: int,
    admin_data: AdministradoraUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza uma administradora"""
    admin = db.query(Administradora).filter(Administradora.id == admin_id).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Administradora não encontrada")

    update_data = admin_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(admin, key, value)

    db.commit()
    db.refresh(admin)
    return admin

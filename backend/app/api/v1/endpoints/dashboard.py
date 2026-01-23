from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.beneficio import Beneficio

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metricas")
async def get_metricas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna métricas para o dashboard"""

    # Total de clientes ativos
    total_clientes = db.query(func.count(Cliente.id)).filter(
        Cliente.ativo == True
    ).scalar() or 0

    # Benefícios por status
    beneficios_stats = db.query(
        Beneficio.status,
        func.count(Beneficio.id).label('total')
    ).filter(
        Beneficio.ativo == True
    ).group_by(Beneficio.status).all()

    status_counts = {stat.status: stat.total for stat in beneficios_stats}

    # Benefícios ativos (não cancelados/rejeitados)
    beneficios_ativos = sum(
        count for status, count in status_counts.items()
        if status not in ['cancelado', 'rejeitado']
    )

    # Contratos pendentes (aguardando assinatura)
    contratos_pendentes = status_counts.get('contrato_gerado', 0)

    # Vendas concluídas (status ativo)
    vendas_concluidas = status_counts.get('ativo', 0)

    # Valor total em créditos ativos
    valor_creditos = db.query(func.sum(Beneficio.valor_credito)).filter(
        Beneficio.ativo == True,
        Beneficio.status == 'ativo'
    ).scalar() or 0

    # Pipeline de vendas (benefícios por status)
    pipeline = [
        {'status': 'rascunho', 'label': 'Rascunho', 'quantidade': status_counts.get('rascunho', 0)},
        {'status': 'proposto', 'label': 'Proposto', 'quantidade': status_counts.get('proposto', 0)},
        {'status': 'aceito', 'label': 'Aceito', 'quantidade': status_counts.get('aceito', 0)},
        {'status': 'contrato_gerado', 'label': 'Contrato Gerado', 'quantidade': status_counts.get('contrato_gerado', 0)},
        {'status': 'contrato_assinado', 'label': 'Contrato Assinado', 'quantidade': status_counts.get('contrato_assinado', 0)},
        {'status': 'aguardando_cadastro', 'label': 'Aguardando Cadastro', 'quantidade': status_counts.get('aguardando_cadastro', 0)},
        {'status': 'cadastrado', 'label': 'Cadastrado', 'quantidade': status_counts.get('cadastrado', 0)},
        {'status': 'termo_gerado', 'label': 'Termo Gerado', 'quantidade': status_counts.get('termo_gerado', 0)},
        {'status': 'ativo', 'label': 'Ativo', 'quantidade': status_counts.get('ativo', 0)},
    ]

    return {
        'total_clientes': total_clientes,
        'beneficios_ativos': beneficios_ativos,
        'contratos_pendentes': contratos_pendentes,
        'vendas_concluidas': vendas_concluidas,
        'valor_creditos': float(valor_creditos),
        'pipeline': pipeline,
    }


@router.get("/atividades-recentes")
async def get_atividades_recentes(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna atividades recentes do sistema"""

    atividades = []

    # Últimos clientes cadastrados
    ultimos_clientes = db.query(Cliente).filter(
        Cliente.ativo == True
    ).order_by(Cliente.created_at.desc()).limit(5).all()

    for cliente in ultimos_clientes:
        atividades.append({
            'tipo': 'cliente',
            'descricao': f'Novo cliente: {cliente.nome}',
            'data': cliente.created_at.isoformat() if cliente.created_at else None,
        })

    # Últimos benefícios criados/atualizados
    ultimos_beneficios = db.query(Beneficio).filter(
        Beneficio.ativo == True
    ).order_by(Beneficio.created_at.desc()).limit(5).all()

    for beneficio in ultimos_beneficios:
        cliente = db.query(Cliente).filter(Cliente.id == beneficio.cliente_id).first()
        cliente_nome = cliente.nome if cliente else 'Cliente'
        atividades.append({
            'tipo': 'beneficio',
            'descricao': f'Benefício #{beneficio.id} - {cliente_nome} ({beneficio.status})',
            'data': beneficio.created_at.isoformat() if beneficio.created_at else None,
        })

    # Ordena por data
    atividades.sort(key=lambda x: x['data'] or '', reverse=True)

    return atividades[:limit]


@router.get("/vendas-por-periodo")
async def get_vendas_por_periodo(
    dias: int = 30,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna vendas agrupadas por dia nos últimos X dias"""

    data_inicio = datetime.utcnow() - timedelta(days=dias)

    # Benefícios criados nos últimos X dias
    beneficios = db.query(
        func.date(Beneficio.created_at).label('data'),
        func.count(Beneficio.id).label('quantidade'),
        func.sum(Beneficio.valor_credito).label('valor')
    ).filter(
        Beneficio.created_at >= data_inicio,
        Beneficio.ativo == True
    ).group_by(
        func.date(Beneficio.created_at)
    ).order_by(
        func.date(Beneficio.created_at)
    ).all()

    return [
        {
            'data': b.data.isoformat() if b.data else None,
            'quantidade': b.quantidade,
            'valor': float(b.valor) if b.valor else 0
        }
        for b in beneficios
    ]


@router.get("/status-distribuicao")
async def get_status_distribuicao(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna distribuição de status para gráfico de pizza"""
    beneficios_stats = db.query(
        Beneficio.status,
        func.count(Beneficio.id).label('total'),
        func.sum(Beneficio.valor_credito).label('valor')
    ).filter(
        Beneficio.ativo == True
    ).group_by(Beneficio.status).all()

    status_labels = {
        'rascunho': 'Rascunho',
        'proposto': 'Proposto',
        'aceito': 'Aceito',
        'rejeitado': 'Rejeitado',
        'contrato_gerado': 'Contrato Gerado',
        'contrato_assinado': 'Contrato Assinado',
        'aguardando_cadastro': 'Aguardando Cadastro',
        'cadastrado': 'Cadastrado',
        'termo_gerado': 'Termo Gerado',
        'ativo': 'Ativo',
        'cancelado': 'Cancelado',
    }

    return [
        {
            'status': stat.status,
            'label': status_labels.get(stat.status, stat.status),
            'quantidade': stat.total,
            'valor': float(stat.valor) if stat.valor else 0
        }
        for stat in beneficios_stats
    ]


@router.get("/tipo-bem-distribuicao")
async def get_tipo_bem_distribuicao(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna distribuição por tipo de bem para gráfico de pizza"""
    stats = db.query(
        Beneficio.tipo_bem,
        func.count(Beneficio.id).label('total'),
        func.sum(Beneficio.valor_credito).label('valor')
    ).filter(
        Beneficio.ativo == True
    ).group_by(Beneficio.tipo_bem).all()

    tipo_labels = {'imovel': 'Imóvel', 'carro': 'Carro', 'moto': 'Moto'}

    return [
        {
            'tipo': stat.tipo_bem,
            'label': tipo_labels.get(stat.tipo_bem, stat.tipo_bem),
            'quantidade': stat.total,
            'valor': float(stat.valor) if stat.valor else 0
        }
        for stat in stats
    ]


@router.get("/vendas-mensal")
async def get_vendas_mensal(
    meses: int = 12,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna vendas agrupadas por mês para gráfico de linha"""
    from dateutil.relativedelta import relativedelta

    data_inicio = datetime.utcnow() - relativedelta(months=meses)

    # SQLite não tem date_trunc, usar strftime
    beneficios = db.query(
        func.strftime('%Y-%m', Beneficio.created_at).label('mes'),
        func.count(Beneficio.id).label('quantidade'),
        func.sum(Beneficio.valor_credito).label('valor')
    ).filter(
        Beneficio.created_at >= data_inicio,
        Beneficio.ativo == True
    ).group_by(
        func.strftime('%Y-%m', Beneficio.created_at)
    ).order_by(
        func.strftime('%Y-%m', Beneficio.created_at)
    ).all()

    # Formatar labels dos meses
    meses_pt = {
        '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr',
        '05': 'Mai', '06': 'Jun', '07': 'Jul', '08': 'Ago',
        '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'
    }

    result = []
    for b in beneficios:
        if b.mes:
            ano, mes = b.mes.split('-')
            mes_label = f"{meses_pt.get(mes, mes)}/{ano[2:]}"
        else:
            mes_label = None

        result.append({
            'mes': b.mes,
            'mes_label': mes_label,
            'quantidade': b.quantidade,
            'valor': float(b.valor) if b.valor else 0
        })

    return result


@router.get("/top-representantes")
async def get_top_representantes(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna top representantes por vendas"""
    stats = db.query(
        Usuario.nome,
        func.count(Beneficio.id).label('total'),
        func.sum(Beneficio.valor_credito).label('valor')
    ).join(
        Beneficio, Beneficio.representante_id == Usuario.id
    ).filter(
        Beneficio.ativo == True
    ).group_by(
        Usuario.id, Usuario.nome
    ).order_by(
        func.count(Beneficio.id).desc()
    ).limit(limit).all()

    return [
        {
            'nome': stat.nome,
            'quantidade': stat.total,
            'valor': float(stat.valor) if stat.valor else 0
        }
        for stat in stats
    ]

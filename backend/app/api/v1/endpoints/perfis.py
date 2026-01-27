from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.models.perfil import Perfil
from app.models.permissao import Permissao, PerfilPermissao
from app.schemas.perfil import (
    PerfilCreate,
    PerfilUpdate,
    PerfilResponse,
    PerfilComPermissoes
)
from app.schemas.permissao import (
    PermissaoResponse,
    PerfilPermissoesUpdate,
    PermissoesMatriz,
    PerfilSimples
)

router = APIRouter(prefix="/perfis", tags=["Perfis"])


# Lista de permissões padrão do sistema
PERMISSOES_PADRAO = [
    # Clientes
    {"codigo": "clientes.criar", "nome": "Criar Cliente", "modulo": "clientes", "descricao": "Permite criar novos clientes"},
    {"codigo": "clientes.editar", "nome": "Editar Cliente", "modulo": "clientes", "descricao": "Permite editar clientes existentes"},
    {"codigo": "clientes.visualizar", "nome": "Visualizar Cliente", "modulo": "clientes", "descricao": "Permite visualizar dados de clientes"},
    {"codigo": "clientes.excluir", "nome": "Excluir Cliente", "modulo": "clientes", "descricao": "Permite desativar clientes"},

    # Benefícios
    {"codigo": "beneficios.criar", "nome": "Criar Benefício", "modulo": "beneficios", "descricao": "Permite criar novos benefícios"},
    {"codigo": "beneficios.editar", "nome": "Editar Benefício", "modulo": "beneficios", "descricao": "Permite editar benefícios existentes"},
    {"codigo": "beneficios.visualizar", "nome": "Visualizar Benefício", "modulo": "beneficios", "descricao": "Permite visualizar benefícios"},
    {"codigo": "beneficios.alterar_status", "nome": "Alterar Status", "modulo": "beneficios", "descricao": "Permite alterar status do benefício"},

    # Contratos
    {"codigo": "contratos.visualizar", "nome": "Visualizar Contrato", "modulo": "contratos", "descricao": "Permite visualizar contratos"},
    {"codigo": "contratos.gerar", "nome": "Gerar Contrato", "modulo": "contratos", "descricao": "Permite gerar novos contratos"},
    {"codigo": "contratos.alterar_status", "nome": "Alterar Status Contrato", "modulo": "contratos", "descricao": "Permite alterar status do contrato"},

    # Relatórios/PDFs
    {"codigo": "relatorios.ficha", "nome": "Gerar Ficha Inicial", "modulo": "relatorios", "descricao": "Permite gerar PDF da ficha inicial"},
    {"codigo": "relatorios.contrato_pdf", "nome": "Gerar PDF Contrato", "modulo": "relatorios", "descricao": "Permite gerar PDF do contrato"},
    {"codigo": "relatorios.termo_pdf", "nome": "Gerar PDF Termo", "modulo": "relatorios", "descricao": "Permite gerar PDF do termo de adesão"},

    # Cadastros
    {"codigo": "cadastros.usuarios", "nome": "Gerenciar Usuários", "modulo": "cadastros", "descricao": "Permite criar/editar usuários"},
    {"codigo": "cadastros.unidades", "nome": "Gerenciar Unidades", "modulo": "cadastros", "descricao": "Permite criar/editar unidades"},
    {"codigo": "cadastros.empresas", "nome": "Gerenciar Empresas", "modulo": "cadastros", "descricao": "Permite criar/editar empresas"},
    {"codigo": "cadastros.representantes", "nome": "Gerenciar Representantes", "modulo": "cadastros", "descricao": "Permite criar/editar representantes"},
    {"codigo": "cadastros.consultores", "nome": "Gerenciar Consultores", "modulo": "cadastros", "descricao": "Permite criar/editar consultores"},
    {"codigo": "cadastros.tabelas_credito", "nome": "Gerenciar Tabelas de Crédito", "modulo": "cadastros", "descricao": "Permite criar/editar tabelas de crédito"},
    {"codigo": "cadastros.administradoras", "nome": "Gerenciar Administradoras", "modulo": "cadastros", "descricao": "Permite criar/editar administradoras"},

    # Configurações
    {"codigo": "configuracoes.sistema", "nome": "Configurações do Sistema", "modulo": "configuracoes", "descricao": "Permite alterar configurações do sistema"},
    {"codigo": "configuracoes.perfis", "nome": "Gerenciar Perfis", "modulo": "configuracoes", "descricao": "Permite gerenciar perfis e permissões"},
]

# Perfis padrão do sistema
PERFIS_PADRAO = [
    {"codigo": "admin", "nome": "Administrador", "descricao": "Acesso total ao sistema", "cor": "#f5222d", "is_system": True},
    {"codigo": "gerente", "nome": "Gerente", "descricao": "Gerenciamento de operações", "cor": "#1890ff", "is_system": True},
    {"codigo": "representante", "nome": "Representante", "descricao": "Vendas e atendimento", "cor": "#52c41a", "is_system": True},
    {"codigo": "consultor", "nome": "Consultor", "descricao": "Apenas visualização", "cor": "#722ed1", "is_system": True},
]

# Permissões padrão por perfil
PERFIL_PERMISSOES_PADRAO = {
    "admin": None,  # Todas
    "gerente": [
        "clientes.criar", "clientes.editar", "clientes.visualizar", "clientes.excluir",
        "beneficios.criar", "beneficios.editar", "beneficios.visualizar", "beneficios.alterar_status",
        "contratos.visualizar", "contratos.gerar", "contratos.alterar_status",
        "relatorios.ficha", "relatorios.contrato_pdf", "relatorios.termo_pdf",
        "cadastros.representantes", "cadastros.consultores",
    ],
    "representante": [
        "clientes.criar", "clientes.editar", "clientes.visualizar",
        "beneficios.criar", "beneficios.editar", "beneficios.visualizar",
        "contratos.visualizar",
        "relatorios.ficha",
    ],
    "consultor": [
        "clientes.visualizar",
        "beneficios.visualizar",
        "contratos.visualizar",
    ],
}


@router.get("/", response_model=List[PerfilResponse])
async def list_perfis(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista todos os perfis"""
    return db.query(Perfil).filter(Perfil.ativo == True).order_by(Perfil.nome).all()


@router.get("/{perfil_id}", response_model=PerfilComPermissoes)
async def get_perfil(
    perfil_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém um perfil com suas permissões"""
    perfil = db.query(Perfil).filter(Perfil.id == perfil_id).first()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")

    # Busca as permissões do perfil
    perfil_perms = db.query(PerfilPermissao).options(
        joinedload(PerfilPermissao.permissao)
    ).filter(
        PerfilPermissao.perfil_id == perfil_id,
        PerfilPermissao.ativo == True
    ).all()

    permissoes = [pp.permissao.codigo for pp in perfil_perms if pp.permissao and pp.permissao.ativo]

    return PerfilComPermissoes(
        id=perfil.id,
        codigo=perfil.codigo,
        nome=perfil.nome,
        descricao=perfil.descricao,
        cor=perfil.cor,
        is_system=perfil.is_system,
        ativo=perfil.ativo,
        created_at=perfil.created_at,
        permissoes=permissoes
    )


@router.post("/", response_model=PerfilComPermissoes, status_code=status.HTTP_201_CREATED)
async def create_perfil(
    data: PerfilCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria um novo perfil"""
    # Verifica se já existe
    existing = db.query(Perfil).filter(Perfil.codigo == data.codigo).first()
    if existing:
        raise HTTPException(status_code=400, detail="Código de perfil já existe")

    # Cria o perfil
    perfil = Perfil(
        codigo=data.codigo,
        nome=data.nome,
        descricao=data.descricao,
        cor=data.cor,
        is_system=False,
        ativo=True
    )
    db.add(perfil)
    db.commit()
    db.refresh(perfil)

    # Adiciona as permissões
    if data.permissoes:
        for codigo in data.permissoes:
            permissao = db.query(Permissao).filter(Permissao.codigo == codigo).first()
            if permissao:
                pp = PerfilPermissao(perfil_id=perfil.id, permissao_id=permissao.id, ativo=True)
                db.add(pp)
        db.commit()

    return await get_perfil(perfil.id, db, current_user)


@router.put("/{perfil_id}", response_model=PerfilComPermissoes)
async def update_perfil(
    perfil_id: int,
    data: PerfilUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza um perfil"""
    perfil = db.query(Perfil).filter(Perfil.id == perfil_id).first()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")

    # Atualiza campos básicos
    if data.nome is not None:
        perfil.nome = data.nome
    if data.descricao is not None:
        perfil.descricao = data.descricao
    if data.cor is not None:
        perfil.cor = data.cor
    if data.ativo is not None:
        perfil.ativo = data.ativo

    # Atualiza permissões se fornecidas
    if data.permissoes is not None:
        # Remove permissões antigas
        db.query(PerfilPermissao).filter(PerfilPermissao.perfil_id == perfil_id).delete()

        # Adiciona novas
        for codigo in data.permissoes:
            permissao = db.query(Permissao).filter(Permissao.codigo == codigo).first()
            if permissao:
                pp = PerfilPermissao(perfil_id=perfil.id, permissao_id=permissao.id, ativo=True)
                db.add(pp)

    db.commit()

    return await get_perfil(perfil.id, db, current_user)


@router.delete("/{perfil_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_perfil(
    perfil_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Exclui um perfil (apenas perfis customizados)"""
    perfil = db.query(Perfil).filter(Perfil.id == perfil_id).first()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")

    if perfil.is_system:
        raise HTTPException(status_code=400, detail="Não é possível excluir perfis do sistema")

    # Verifica se há usuários com esse perfil
    usuarios_count = db.query(Usuario).filter(Usuario.perfil_id == perfil_id).count()
    if usuarios_count > 0:
        raise HTTPException(status_code=400, detail=f"Existem {usuarios_count} usuários com esse perfil")

    # Remove permissões e o perfil
    db.query(PerfilPermissao).filter(PerfilPermissao.perfil_id == perfil_id).delete()
    db.delete(perfil)
    db.commit()

    return None


@router.get("/permissoes/todas", response_model=List[PermissaoResponse])
async def list_permissoes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista todas as permissões disponíveis"""
    return db.query(Permissao).filter(Permissao.ativo == True).order_by(Permissao.modulo, Permissao.nome).all()


@router.get("/permissoes/matriz", response_model=PermissoesMatriz)
async def get_matriz_permissoes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna a matriz de permissões (permissões x perfis)"""
    # Busca todas as permissões
    permissoes = db.query(Permissao).filter(Permissao.ativo == True).order_by(Permissao.modulo, Permissao.nome).all()

    # Busca todos os perfis
    perfis = db.query(Perfil).filter(Perfil.ativo == True).order_by(Perfil.nome).all()

    # Busca todas as relações perfil-permissão
    perfil_permissoes = db.query(PerfilPermissao).options(
        joinedload(PerfilPermissao.permissao)
    ).filter(PerfilPermissao.ativo == True).all()

    # Monta a matriz
    matriz = {}
    for perfil in perfis:
        matriz[str(perfil.id)] = []

    for pp in perfil_permissoes:
        if pp.permissao and pp.permissao.ativo:
            perfil_key = str(pp.perfil_id)
            if perfil_key not in matriz:
                matriz[perfil_key] = []
            matriz[perfil_key].append(pp.permissao.codigo)

    return PermissoesMatriz(
        permissoes=[PermissaoResponse.model_validate(p) for p in permissoes],
        perfis=[PerfilSimples.model_validate(p) for p in perfis],
        matriz=matriz
    )


@router.put("/{perfil_id}/permissoes")
async def update_perfil_permissoes(
    perfil_id: int,
    data: PerfilPermissoesUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza apenas as permissões de um perfil"""
    perfil = db.query(Perfil).filter(Perfil.id == perfil_id).first()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")

    # Remove permissões antigas
    db.query(PerfilPermissao).filter(PerfilPermissao.perfil_id == perfil_id).delete()

    # Adiciona novas
    for codigo in data.permissoes:
        permissao = db.query(Permissao).filter(Permissao.codigo == codigo).first()
        if permissao:
            pp = PerfilPermissao(perfil_id=perfil.id, permissao_id=permissao.id, ativo=True)
            db.add(pp)

    db.commit()

    return {"message": f"Permissões do perfil {perfil.nome} atualizadas com sucesso"}


@router.post("/seed")
async def seed_perfis(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Popula perfis e permissões padrão do sistema"""
    # Verifica se já existem perfis
    existing_perfis = db.query(Perfil).count()
    if existing_perfis > 0:
        return {"message": "Perfis já foram populados", "count": existing_perfis}

    # Cria as permissões
    existing_perms = db.query(Permissao).count()
    if existing_perms == 0:
        for p in PERMISSOES_PADRAO:
            permissao = Permissao(**p, ativo=True)
            db.add(permissao)
        db.commit()

    # Busca as permissões criadas
    all_perms = {p.codigo: p.id for p in db.query(Permissao).all()}

    # Cria os perfis
    perfil_ids = {}
    for p in PERFIS_PADRAO:
        perfil = Perfil(**p, ativo=True)
        db.add(perfil)
        db.commit()
        db.refresh(perfil)
        perfil_ids[perfil.codigo] = perfil.id

    # Cria as associações perfil-permissão
    for perfil_codigo, codigos in PERFIL_PERMISSOES_PADRAO.items():
        perfil_id = perfil_ids.get(perfil_codigo)
        if not perfil_id:
            continue

        if codigos is None:
            # Admin tem todas
            codigos = list(all_perms.keys())

        for codigo in codigos:
            if codigo in all_perms:
                pp = PerfilPermissao(
                    perfil_id=perfil_id,
                    permissao_id=all_perms[codigo],
                    ativo=True
                )
                db.add(pp)

    db.commit()

    return {
        "message": "Perfis e permissões criados com sucesso",
        "perfis_criados": len(PERFIS_PADRAO),
        "permissoes_criadas": len(PERMISSOES_PADRAO)
    }


@router.get("/usuario/minhas-permissoes")
async def get_minhas_permissoes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna as permissões do usuário logado"""
    perfil = db.query(Perfil).filter(Perfil.id == current_user.perfil_id).first()
    if not perfil:
        return {"perfil": None, "permissoes": []}

    # Admin tem todas
    if perfil.codigo == "admin":
        permissoes = db.query(Permissao).filter(Permissao.ativo == True).all()
        return {
            "perfil": PerfilSimples.model_validate(perfil),
            "permissoes": [p.codigo for p in permissoes]
        }

    # Busca permissões do perfil
    perfil_permissoes = db.query(PerfilPermissao).options(
        joinedload(PerfilPermissao.permissao)
    ).filter(
        PerfilPermissao.perfil_id == current_user.perfil_id,
        PerfilPermissao.ativo == True
    ).all()

    return {
        "perfil": PerfilSimples.model_validate(perfil),
        "permissoes": [pp.permissao.codigo for pp in perfil_permissoes if pp.permissao and pp.permissao.ativo]
    }


def has_permission(db: Session, user: Usuario, codigo_permissao: str) -> bool:
    """Verifica se o usuário tem uma permissão específica"""
    perfil = db.query(Perfil).filter(Perfil.id == user.perfil_id).first()
    if not perfil:
        return False

    # Admin sempre tem todas as permissões
    if perfil.codigo == "admin":
        return True

    # Busca a permissão pelo código
    permissao = db.query(Permissao).filter(Permissao.codigo == codigo_permissao).first()
    if not permissao:
        return False

    # Verifica se o perfil do usuário tem essa permissão
    pp = db.query(PerfilPermissao).filter(
        PerfilPermissao.perfil_id == user.perfil_id,
        PerfilPermissao.permissao_id == permissao.id,
        PerfilPermissao.ativo == True
    ).first()

    return pp is not None


def check_permission(codigo_permissao: str):
    """Dependency para verificar permissão em endpoints"""
    async def permission_checker(
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user)
    ):
        if not has_permission(db, current_user, codigo_permissao):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Sem permissão: {codigo_permissao}"
            )
        return current_user
    return permission_checker

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router
# Importar todos os models para garantir que sejam registrados
from app.models import *  # noqa: F401, F403

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown events"""
    # Startup: criar tabelas do banco
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: nada a fazer


# Cria aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema CRM para gestão de consórcios",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - permite origens configuradas + todas em desenvolvimento
cors_origins = settings.cors_origins_list if not settings.DEBUG else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https://.*\.onrender\.com",  # Permite qualquer subdomínio do Render
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui rotas da API
app.include_router(api_router)


@app.get("/")
async def root():
    """Endpoint de health check"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/debug/db")
async def debug_db():
    """Debug endpoint para verificar estado do banco"""
    from sqlalchemy import text, inspect
    from app.core.database import engine

    result = {
        "deploy_version": "2026-01-27-v8",
        "database_url_masked": settings.DATABASE_URL[:30] + "..." if len(settings.DATABASE_URL) > 30 else "short",
    }

    try:
        with engine.connect() as conn:
            # Verifica tabelas existentes
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            result["tables"] = tables

            # Verifica colunas da tabela usuarios
            if "usuarios" in tables:
                columns = [col["name"] for col in inspector.get_columns("usuarios")]
                result["usuarios_columns"] = columns

            # Verifica versão do alembic
            if "alembic_version" in tables:
                version = conn.execute(text("SELECT version_num FROM alembic_version")).fetchone()
                result["alembic_version"] = version[0] if version else None
            else:
                result["alembic_version"] = "table not found"

            # Verifica se tabela perfis existe
            result["perfis_exists"] = "perfis" in tables

    except Exception as e:
        result["error"] = str(e)

    return result


@app.post("/debug/fix-usuarios")
async def fix_usuarios():
    """Corrige a tabela usuarios adicionando perfil_id"""
    from sqlalchemy import text
    from app.core.database import engine

    steps = []

    try:
        with engine.connect() as conn:
            # 1. Verifica estado atual
            from sqlalchemy import inspect
            inspector = inspect(engine)
            columns = [col["name"] for col in inspector.get_columns("usuarios")]

            # 2. Insere perfis padrão se não existirem
            result = conn.execute(text("SELECT COUNT(*) FROM perfis"))
            count = result.fetchone()[0]
            if count == 0:
                conn.execute(text("""
                    INSERT INTO perfis (id, codigo, nome, descricao, cor, is_system, ativo)
                    VALUES
                    (1, 'admin', 'Administrador', 'Acesso total ao sistema', '#f5222d', true, true),
                    (2, 'gerente', 'Gerente', 'Gerente de unidade', '#fa8c16', true, true),
                    (3, 'vendedor', 'Vendedor', 'Vendedor/Representante', '#1890ff', true, true),
                    (4, 'consultor', 'Consultor', 'Consultor de vendas', '#52c41a', true, true)
                """))
                conn.commit()
                steps.append("inserted default perfis")
            else:
                steps.append(f"perfis table has {count} records")

            # 3. Adiciona coluna perfil_id (se não existir)
            if "perfil_id" not in columns:
                conn.execute(text("ALTER TABLE usuarios ADD COLUMN perfil_id INTEGER"))
                conn.commit()
                steps.append("added perfil_id column")
            else:
                steps.append("perfil_id column already exists")

            # 4. Atualiza perfil_id baseado em perfil (cast enum to text)
            # Só atualiza onde perfil_id é NULL
            result = conn.execute(text("""
                UPDATE usuarios SET perfil_id =
                    CASE perfil::text
                        WHEN 'admin' THEN 1
                        WHEN 'gerente' THEN 2
                        WHEN 'vendedor' THEN 3
                        WHEN 'representante' THEN 3
                        WHEN 'consultor' THEN 4
                        ELSE 3
                    END
                WHERE perfil_id IS NULL
            """))
            conn.commit()
            steps.append(f"updated {result.rowcount} perfil_id values")

            # 5. Adiciona FK (se não existir)
            try:
                conn.execute(text("""
                    ALTER TABLE usuarios
                    ADD CONSTRAINT fk_usuarios_perfil_id
                    FOREIGN KEY (perfil_id) REFERENCES perfis(id)
                """))
                conn.commit()
                steps.append("added foreign key")
            except Exception as e:
                if "already exists" in str(e).lower():
                    steps.append("foreign key already exists")
                else:
                    raise

            # 6. Remove coluna antiga perfil (opcional - mantém por segurança)
            # conn.execute(text("ALTER TABLE usuarios DROP COLUMN perfil"))
            # steps.append("dropped perfil column")

            # 7. Cria tabela alembic_version e marca como migrado
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS alembic_version (
                    version_num VARCHAR(32) NOT NULL,
                    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                )
            """))
            conn.commit()
            conn.execute(text("DELETE FROM alembic_version"))
            conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('006')"))
            conn.commit()
            steps.append("created alembic_version and stamped to 006")

        return {"status": "success", "steps": steps}

    except Exception as e:
        import traceback
        return {"status": "error", "error": str(e), "steps": steps, "trace": traceback.format_exc()}


@app.get("/debug/unidades-table")
async def debug_unidades_table():
    """Verifica estrutura da tabela unidades"""
    from sqlalchemy import text, inspect
    from app.core.database import engine

    result = {}
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            result["unidades_exists"] = "unidades" in tables
            result["empresas_exists"] = "empresas" in tables

            if "unidades" in tables:
                columns = [{"name": col["name"], "type": str(col["type"])} for col in inspector.get_columns("unidades")]
                result["unidades_columns"] = columns

            if "empresas" in tables:
                empresas_count = conn.execute(text("SELECT COUNT(*) FROM empresas")).fetchone()[0]
                result["empresas_count"] = empresas_count

            # Verifica se há unidades
            if "unidades" in tables:
                unidades_count = conn.execute(text("SELECT COUNT(*) FROM unidades")).fetchone()[0]
                result["unidades_count"] = unidades_count

    except Exception as e:
        import traceback
        result["error"] = str(e)
        result["trace"] = traceback.format_exc()

    return result


@app.post("/debug/create-unidade")
async def debug_create_unidade():
    """Tenta criar unidade com detalhes de erro"""
    from sqlalchemy import text
    from app.core.database import engine

    result = {"steps": []}

    try:
        with engine.connect() as conn:
            # 1. Verifica se codigo já existe
            existing = conn.execute(text("SELECT id FROM unidades WHERE codigo = 'TEST001'")).fetchone()
            if existing:
                result["steps"].append(f"codigo TEST001 already exists with id {existing[0]}")
                return result

            # 2. Tenta inserir
            conn.execute(text("""
                INSERT INTO unidades (nome, codigo, ativo)
                VALUES ('Unidade Teste Debug', 'TEST001', true)
            """))
            conn.commit()
            result["steps"].append("inserted unidade successfully")

            # 3. Verifica se foi inserida
            new_unidade = conn.execute(text("SELECT id, nome, codigo FROM unidades WHERE codigo = 'TEST001'")).fetchone()
            if new_unidade:
                result["steps"].append(f"created unidade: id={new_unidade[0]}, nome={new_unidade[1]}")
                result["unidade_id"] = new_unidade[0]

        result["status"] = "success"

    except Exception as e:
        import traceback
        result["status"] = "error"
        result["error"] = str(e)
        result["trace"] = traceback.format_exc()

    return result


@app.post("/debug/seed-permissoes")
async def seed_permissoes():
    """Popula a tabela de permissões"""
    from sqlalchemy import text
    from app.core.database import engine

    PERMISSOES = [
        ("clientes.criar", "Criar Cliente", "clientes"),
        ("clientes.editar", "Editar Cliente", "clientes"),
        ("clientes.visualizar", "Visualizar Cliente", "clientes"),
        ("clientes.excluir", "Excluir Cliente", "clientes"),
        ("beneficios.criar", "Criar Benefício", "beneficios"),
        ("beneficios.editar", "Editar Benefício", "beneficios"),
        ("beneficios.visualizar", "Visualizar Benefício", "beneficios"),
        ("beneficios.alterar_status", "Alterar Status", "beneficios"),
        ("contratos.visualizar", "Visualizar Contrato", "contratos"),
        ("contratos.gerar", "Gerar Contrato", "contratos"),
        ("contratos.alterar_status", "Alterar Status Contrato", "contratos"),
        ("relatorios.ficha", "Gerar Ficha Inicial", "relatorios"),
        ("relatorios.contrato_pdf", "Gerar PDF Contrato", "relatorios"),
        ("relatorios.termo_pdf", "Gerar PDF Termo", "relatorios"),
        ("cadastros.usuarios", "Gerenciar Usuários", "cadastros"),
        ("cadastros.unidades", "Gerenciar Unidades", "cadastros"),
        ("cadastros.empresas", "Gerenciar Empresas", "cadastros"),
        ("cadastros.representantes", "Gerenciar Representantes", "cadastros"),
        ("cadastros.consultores", "Gerenciar Consultores", "cadastros"),
        ("cadastros.tabelas_credito", "Gerenciar Tabelas de Crédito", "cadastros"),
        ("cadastros.administradoras", "Gerenciar Administradoras", "cadastros"),
        ("configuracoes.sistema", "Configurações do Sistema", "configuracoes"),
        ("configuracoes.perfis", "Gerenciar Perfis", "configuracoes"),
    ]

    steps = []

    try:
        with engine.connect() as conn:
            # Verifica se já tem permissões
            result = conn.execute(text("SELECT COUNT(*) FROM permissoes"))
            count = result.fetchone()[0]

            if count > 0:
                return {"status": "already_seeded", "count": count}

            # Insere as permissões
            for codigo, nome, modulo in PERMISSOES:
                conn.execute(text("""
                    INSERT INTO permissoes (codigo, nome, modulo, ativo)
                    VALUES (:codigo, :nome, :modulo, true)
                """), {"codigo": codigo, "nome": nome, "modulo": modulo})

            conn.commit()
            steps.append(f"inserted {len(PERMISSOES)} permissions")

            # Associa todas as permissões ao perfil admin (id=1)
            result = conn.execute(text("SELECT id FROM permissoes"))
            perm_ids = [row[0] for row in result.fetchall()]

            for perm_id in perm_ids:
                conn.execute(text("""
                    INSERT INTO perfil_permissoes (perfil_id, permissao_id, ativo)
                    VALUES (1, :perm_id, true)
                """), {"perm_id": perm_id})

            conn.commit()
            steps.append(f"linked {len(perm_ids)} permissions to admin profile")

        return {"status": "success", "steps": steps}

    except Exception as e:
        import traceback
        return {"status": "error", "error": str(e), "steps": steps, "trace": traceback.format_exc()}

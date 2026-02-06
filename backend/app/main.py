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


def seed_initial_data():
    """Cria dados iniciais no banco (perfis, permissões, admin)"""
    from sqlalchemy.orm import Session
    from app.core.database import SessionLocal
    from app.models.perfil import Perfil
    from app.models.usuario import Usuario
    from app.models.permissao import Permissao
    import bcrypt

    db = SessionLocal()
    try:
        # 1. Criar perfis padrão
        if db.query(Perfil).count() == 0:
            perfis = [
                Perfil(id=1, codigo='admin', nome='Administrador', descricao='Acesso total ao sistema', cor='#f5222d', is_system=True, ativo=True),
                Perfil(id=2, codigo='gerente', nome='Gerente', descricao='Gerente de unidade', cor='#fa8c16', is_system=True, ativo=True),
                Perfil(id=3, codigo='vendedor', nome='Vendedor', descricao='Vendedor/Representante', cor='#1890ff', is_system=True, ativo=True),
                Perfil(id=4, codigo='consultor', nome='Consultor', descricao='Consultor de vendas', cor='#52c41a', is_system=True, ativo=True),
            ]
            for p in perfis:
                db.add(p)
            db.commit()
            print("✓ Perfis criados")

        # 2. Criar permissões
        if db.query(Permissao).count() == 0:
            permissoes = [
                ("clientes.criar", "Criar Cliente", "clientes"),
                ("clientes.editar", "Editar Cliente", "clientes"),
                ("clientes.visualizar", "Visualizar Cliente", "clientes"),
                ("clientes.excluir", "Excluir Cliente", "clientes"),
                ("beneficios.criar", "Criar Benefício", "beneficios"),
                ("beneficios.editar", "Editar Benefício", "beneficios"),
                ("beneficios.visualizar", "Visualizar Benefício", "beneficios"),
                ("beneficios.alterar_status", "Alterar Status", "beneficios"),
                ("cadastros.usuarios", "Gerenciar Usuários", "cadastros"),
                ("cadastros.unidades", "Gerenciar Unidades", "cadastros"),
                ("cadastros.empresas", "Gerenciar Empresas", "cadastros"),
                ("configuracoes.sistema", "Configurações do Sistema", "configuracoes"),
                ("configuracoes.perfis", "Gerenciar Perfis", "configuracoes"),
            ]
            for codigo, nome, modulo in permissoes:
                db.add(Permissao(codigo=codigo, nome=nome, modulo=modulo, ativo=True))
            db.commit()
            print("✓ Permissões criadas")

        # 3. Criar usuário admin
        if not db.query(Usuario).filter(Usuario.email == "ivis_ribeiro@hotmail.com").first():
            senha_hash = bcrypt.hashpw(b"admin@123", bcrypt.gensalt()).decode('utf-8')
            admin = Usuario(
                nome="Ivis Ribeiro",
                email="ivis_ribeiro@hotmail.com",
                senha_hash=senha_hash,
                perfil_id=1,
                ativo=True
            )
            db.add(admin)
            db.commit()
            print("✓ Admin criado: ivis_ribeiro@hotmail.com")

    except Exception as e:
        print(f"Erro no seed: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown events"""
    # Startup: criar tabelas do banco
    Base.metadata.create_all(bind=engine)
    # Seed dados iniciais
    seed_initial_data()
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
    allow_origin_regex=r"https://.*\.(onrender\.com|railway\.app|up\.railway\.app)",  # Render e Railway
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
        "deploy_version": "2026-01-28-v9",
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

            # 6. Remove coluna antiga perfil (necessário para novos inserts)
            if "perfil" in columns:
                conn.execute(text("ALTER TABLE usuarios DROP COLUMN perfil"))
                conn.commit()
                steps.append("dropped old perfil column")
            else:
                steps.append("perfil column already removed")

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


@app.get("/debug/tabelas-credito-table")
async def debug_tabelas_credito_table():
    """Verifica estrutura da tabela tabelas_credito"""
    from sqlalchemy import text, inspect
    from app.core.database import engine

    result = {}
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            result["table_exists"] = "tabelas_credito" in tables

            if "tabelas_credito" in tables:
                columns = [{"name": col["name"], "type": str(col["type"])} for col in inspector.get_columns("tabelas_credito")]
                result["columns"] = columns

                count = conn.execute(text("SELECT COUNT(*) FROM tabelas_credito")).fetchone()[0]
                result["count"] = count
            else:
                result["message"] = "Table does not exist"

    except Exception as e:
        import traceback
        result["error"] = str(e)
        result["trace"] = traceback.format_exc()

    return result


@app.post("/debug/fix-clientes-table")
async def fix_clientes_table():
    """Corrige a coluna taxa_inicial na tabela clientes (Numeric(5,2) -> Numeric(12,2))"""
    from sqlalchemy import text
    from app.core.database import engine

    result = {"steps": []}
    try:
        with engine.connect() as conn:
            # Altera o tipo da coluna taxa_inicial
            conn.execute(text("""
                ALTER TABLE clientes
                ALTER COLUMN taxa_inicial TYPE NUMERIC(12, 2)
            """))
            conn.commit()
            result["steps"].append("changed taxa_inicial from Numeric(5,2) to Numeric(12,2)")

        result["status"] = "success"
    except Exception as e:
        import traceback
        result["status"] = "error"
        result["error"] = str(e)
        result["trace"] = traceback.format_exc()

    return result


@app.post("/debug/fix-tabelas-credito")
async def fix_tabelas_credito_table():
    """Adiciona coluna administradora_id na tabela tabelas_credito se não existir"""
    from sqlalchemy import text, inspect
    from app.core.database import engine

    result = {"steps": []}
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)

            if "tabelas_credito" in inspector.get_table_names():
                columns = [col["name"] for col in inspector.get_columns("tabelas_credito")]

                if "administradora_id" not in columns:
                    conn.execute(text("""
                        ALTER TABLE tabelas_credito
                        ADD COLUMN administradora_id INTEGER REFERENCES administradoras(id)
                    """))
                    conn.commit()
                    result["steps"].append("added administradora_id column")
                else:
                    result["steps"].append("administradora_id column already exists")
            else:
                # Create table if not exists
                conn.execute(text("""
                    CREATE TABLE tabelas_credito (
                        id SERIAL PRIMARY KEY,
                        nome VARCHAR(100) NOT NULL,
                        tipo_bem VARCHAR(20) NOT NULL,
                        prazo INTEGER NOT NULL,
                        valor_credito NUMERIC(12,2) NOT NULL,
                        parcela NUMERIC(12,2) NOT NULL,
                        fundo_reserva NUMERIC(5,2) DEFAULT 2.5,
                        taxa_administracao NUMERIC(5,2) DEFAULT 26.0,
                        seguro_prestamista NUMERIC(5,2) DEFAULT 0.0,
                        indice_correcao VARCHAR(20) DEFAULT 'INCC',
                        qtd_participantes INTEGER DEFAULT 4076,
                        tipo_plano VARCHAR(50) DEFAULT 'Normal',
                        ativo BOOLEAN DEFAULT true,
                        administradora_id INTEGER REFERENCES administradoras(id),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE
                    )
                """))
                conn.commit()
                result["steps"].append("created tabelas_credito table")

        result["status"] = "success"
    except Exception as e:
        import traceback
        result["status"] = "error"
        result["error"] = str(e)
        result["trace"] = traceback.format_exc()

    return result


@app.post("/debug/drop-perfil-column")
async def drop_perfil_column():
    """Remove a coluna perfil antiga (enum) da tabela usuarios"""
    from sqlalchemy import text, inspect
    from app.core.database import engine

    result = {"steps": []}
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            columns = [col["name"] for col in inspector.get_columns("usuarios")]
            result["columns_before"] = columns

            if "perfil" in columns:
                # Drop the old enum column
                conn.execute(text("ALTER TABLE usuarios DROP COLUMN IF EXISTS perfil"))
                conn.commit()
                result["steps"].append("dropped perfil column")

                # Also drop the enum type if it exists
                try:
                    conn.execute(text("DROP TYPE IF EXISTS perfilusuario"))
                    conn.commit()
                    result["steps"].append("dropped perfilusuario enum type")
                except Exception as e:
                    result["steps"].append(f"enum drop skipped: {str(e)[:50]}")

            else:
                result["steps"].append("perfil column does not exist")

            # Re-check columns
            columns_after = [col["name"] for col in inspector.get_columns("usuarios")]
            result["columns_after"] = columns_after

        result["status"] = "success"
    except Exception as e:
        import traceback
        result["status"] = "error"
        result["error"] = str(e)
        result["trace"] = traceback.format_exc()

    return result


@app.get("/debug/usuarios-table")
async def debug_usuarios_table():
    """Verifica estrutura completa da tabela usuarios"""
    from sqlalchemy import text, inspect
    from app.core.database import engine

    result = {}
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            columns = []
            for col in inspector.get_columns("usuarios"):
                columns.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True)
                })
            result["columns"] = columns

            # Verifica se existe constraint na coluna perfil
            result["has_perfil_column"] = any(c["name"] == "perfil" for c in columns)
            result["has_perfil_id_column"] = any(c["name"] == "perfil_id" for c in columns)

    except Exception as e:
        import traceback
        result["error"] = str(e)
        result["trace"] = traceback.format_exc()

    return result


@app.post("/debug/fix-usuarios-perfil")
async def fix_usuarios_perfil():
    """Remove a coluna perfil antiga da tabela usuarios"""
    from sqlalchemy import text, inspect
    from app.core.database import engine

    result = {"steps": []}
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            columns = [col["name"] for col in inspector.get_columns("usuarios")]

            if "perfil" in columns:
                # Remove a coluna perfil antiga
                conn.execute(text("ALTER TABLE usuarios DROP COLUMN perfil"))
                conn.commit()
                result["steps"].append("dropped perfil column")
            else:
                result["steps"].append("perfil column does not exist")

            # Verifica colunas após
            columns_after = [col["name"] for col in inspector.get_columns("usuarios")]
            result["columns_after"] = columns_after

        result["status"] = "success"

    except Exception as e:
        import traceback
        result["status"] = "error"
        result["error"] = str(e)
        result["trace"] = traceback.format_exc()

    return result


@app.post("/debug/fix-unidades-table")
async def fix_unidades_table():
    """Adiciona coluna empresa_id na tabela unidades se não existir"""
    from sqlalchemy import text, inspect
    from app.core.database import engine

    result = {"steps": []}

    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            columns = [col["name"] for col in inspector.get_columns("unidades")]
            result["current_columns"] = columns

            # Adiciona empresa_id se não existir
            if "empresa_id" not in columns:
                conn.execute(text("""
                    ALTER TABLE unidades ADD COLUMN empresa_id INTEGER REFERENCES empresas(id)
                """))
                conn.commit()
                result["steps"].append("added empresa_id column")
            else:
                result["steps"].append("empresa_id column already exists")

            # Verifica colunas atualizadas
            columns_after = [col["name"] for col in inspector.get_columns("unidades")]
            result["columns_after"] = columns_after

        result["status"] = "success"

    except Exception as e:
        import traceback
        result["status"] = "error"
        result["error"] = str(e)
        result["trace"] = traceback.format_exc()

    return result


@app.post("/debug/fix-perfil-permissoes-table")
async def fix_perfil_permissoes_table():
    """Recria a tabela perfil_permissoes com estrutura correta"""
    from sqlalchemy import text
    from app.core.database import engine

    result = {"steps": []}
    try:
        with engine.connect() as conn:
            # Drop e recria a tabela
            conn.execute(text("DROP TABLE IF EXISTS perfil_permissoes CASCADE"))
            conn.commit()
            result["steps"].append("dropped perfil_permissoes")

            conn.execute(text("""
                CREATE TABLE perfil_permissoes (
                    id SERIAL PRIMARY KEY,
                    perfil_id INTEGER NOT NULL REFERENCES perfis(id),
                    permissao_id INTEGER NOT NULL REFERENCES permissoes(id),
                    ativo BOOLEAN DEFAULT true,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            conn.commit()
            result["steps"].append("created perfil_permissoes table")

            # Criar índices
            conn.execute(text("CREATE INDEX ix_perfil_permissoes_perfil_id ON perfil_permissoes(perfil_id)"))
            conn.commit()
            result["steps"].append("created index")

            # Associar todas as permissões ao perfil admin (id=1)
            r = conn.execute(text("SELECT id FROM permissoes WHERE ativo = true"))
            perm_ids = [row[0] for row in r.fetchall()]

            for perm_id in perm_ids:
                conn.execute(text("""
                    INSERT INTO perfil_permissoes (perfil_id, permissao_id, ativo)
                    VALUES (1, :perm_id, true)
                """), {"perm_id": perm_id})
            conn.commit()
            result["steps"].append(f"linked {len(perm_ids)} permissions to admin")

        result["status"] = "success"
    except Exception as e:
        import traceback
        result["status"] = "error"
        result["error"] = str(e)
        result["trace"] = traceback.format_exc()

    return result


@app.post("/debug/fix-perfis-editable")
async def fix_perfis_editable():
    """Atualiza perfis para serem editáveis/excluíveis (is_system=False)"""
    from sqlalchemy import text
    from app.core.database import engine

    result = {"steps": []}
    try:
        with engine.connect() as conn:
            # Atualiza todos os perfis para is_system=False (exceto admin que fica protegido)
            r = conn.execute(text("""
                UPDATE perfis SET is_system = false WHERE codigo != 'admin'
            """))
            conn.commit()
            result["steps"].append(f"updated {r.rowcount} perfis to is_system=false")

        result["status"] = "success"
    except Exception as e:
        import traceback
        result["status"] = "error"
        result["error"] = str(e)
        result["trace"] = traceback.format_exc()

    return result


@app.post("/debug/fix-tabelas-credito-intermediacao")
async def fix_tabelas_credito_intermediacao():
    """Adiciona coluna valor_intermediacao na tabela tabelas_credito"""
    from sqlalchemy import text, inspect
    from app.core.database import engine

    result = {"steps": []}
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            columns = [col["name"] for col in inspector.get_columns("tabelas_credito")]

            if "valor_intermediacao" not in columns:
                conn.execute(text("""
                    ALTER TABLE tabelas_credito
                    ADD COLUMN valor_intermediacao NUMERIC(12,2) DEFAULT 0
                """))
                conn.commit()
                result["steps"].append("added valor_intermediacao column")
            else:
                result["steps"].append("valor_intermediacao already exists")

        result["status"] = "success"
    except Exception as e:
        import traceback
        result["status"] = "error"
        result["error"] = str(e)
        result["trace"] = traceback.format_exc()

    return result


@app.post("/debug/reset-database")
async def reset_database():
    """
    Reseta o banco de dados:
    - Trunca todas as tabelas (exceto usuarios, perfis, permissoes)
    - Cria/atualiza usuário admin ivis_ribeiro@hotmail.com
    """
    from sqlalchemy import text
    from app.core.database import engine
    import bcrypt

    steps = []

    try:
        with engine.connect() as conn:
            # 1. Truncar tabelas de dados (ordem importa por causa das FKs)
            tables_to_truncate = [
                'beneficio_faixas',
                'beneficio_historicos',
                'beneficios',
                'clientes',
                'tabelas_credito',
                'administradoras',
                'representantes',
                'consultores',
                'configuracoes',
                'unidades',
                'empresas',
            ]

            for table in tables_to_truncate:
                try:
                    conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
                    steps.append(f"truncated {table}")
                except Exception as e:
                    steps.append(f"skip {table}: {str(e)[:30]}")

            conn.commit()

            # 2. Limpar usuarios (exceto admin)
            conn.execute(text("DELETE FROM usuarios WHERE email != 'ivis_ribeiro@hotmail.com'"))
            conn.commit()
            steps.append("deleted non-admin users")

            # 3. Criar/atualizar admin
            result = conn.execute(text("SELECT id FROM usuarios WHERE email = 'ivis_ribeiro@hotmail.com'"))
            admin_row = result.fetchone()

            senha_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode('utf-8')

            if admin_row:
                conn.execute(text("""
                    UPDATE usuarios SET senha_hash = :senha, nome = 'Ivis Ribeiro', perfil_id = 1, ativo = true
                    WHERE email = 'ivis_ribeiro@hotmail.com'
                """), {"senha": senha_hash})
                steps.append("updated admin password to admin123")
            else:
                conn.execute(text("""
                    INSERT INTO usuarios (nome, email, senha_hash, perfil_id, ativo)
                    VALUES ('Ivis Ribeiro', 'ivis_ribeiro@hotmail.com', :senha, 1, true)
                """), {"senha": senha_hash})
                steps.append("created admin user")

            conn.commit()

            # 4. Criar unidade padrão (necessária para o sistema)
            conn.execute(text("""
                INSERT INTO unidades (id, nome, codigo, ativo)
                VALUES (1, 'Matriz', 'MTZ', true)
                ON CONFLICT (id) DO NOTHING
            """))
            conn.commit()
            steps.append("created default unidade")

            # 5. Atualizar unidade_id do admin
            conn.execute(text("""
                UPDATE usuarios SET unidade_id = 1 WHERE email = 'ivis_ribeiro@hotmail.com'
            """))
            conn.commit()
            steps.append("linked admin to unidade")

        return {"status": "success", "steps": steps, "login": {"email": "ivis_ribeiro@hotmail.com", "senha": "admin123"}}

    except Exception as e:
        import traceback
        return {"status": "error", "error": str(e), "steps": steps, "trace": traceback.format_exc()}


@app.post("/debug/fix-beneficios-representante")
async def fix_beneficios_representante():
    """Corrige a FK representante_id na tabela beneficios (de usuarios para representantes)"""
    from sqlalchemy import text, inspect
    from app.core.database import engine

    result = {"steps": []}
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)

            # Verifica se tabela beneficios existe
            if "beneficios" not in inspector.get_table_names():
                result["steps"].append("beneficios table does not exist")
                result["status"] = "error"
                return result

            # 1. Remove a FK antiga (se existir)
            try:
                conn.execute(text("""
                    ALTER TABLE beneficios DROP CONSTRAINT IF EXISTS beneficios_representante_id_fkey
                """))
                conn.commit()
                result["steps"].append("dropped old FK constraint")
            except Exception as e:
                result["steps"].append(f"drop FK skipped: {str(e)[:50]}")

            # 2. Limpa valores inválidos (seta NULL onde representante_id não existe em representantes)
            try:
                conn.execute(text("""
                    UPDATE beneficios SET representante_id = NULL
                    WHERE representante_id IS NOT NULL
                    AND representante_id NOT IN (SELECT id FROM representantes)
                """))
                conn.commit()
                result["steps"].append("cleared invalid representante_id values")
            except Exception as e:
                result["steps"].append(f"clear values skipped: {str(e)[:50]}")

            # 3. Adiciona nova FK para representantes
            try:
                conn.execute(text("""
                    ALTER TABLE beneficios
                    ADD CONSTRAINT beneficios_representante_id_fkey
                    FOREIGN KEY (representante_id) REFERENCES representantes(id)
                """))
                conn.commit()
                result["steps"].append("added new FK to representantes table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    result["steps"].append("FK already exists")
                else:
                    result["steps"].append(f"add FK error: {str(e)[:50]}")

            # 4. Verifica estado final
            columns = [col["name"] for col in inspector.get_columns("beneficios")]
            result["beneficios_columns"] = columns

            # Conta representantes
            rep_count = conn.execute(text("SELECT COUNT(*) FROM representantes")).fetchone()[0]
            result["representantes_count"] = rep_count

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

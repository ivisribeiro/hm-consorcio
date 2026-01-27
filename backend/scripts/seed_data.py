"""
Script para popular o banco de dados com dados iniciais
"""
import sys
import os
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.usuario import Usuario
from app.models.unidade import Unidade
from app.models.empresa import Empresa
from app.models.tabela_credito import TabelaCredito
from app.models.administradora import Administradora


def seed_unidades(db: Session):
    unidades = [
        Unidade(nome="Matriz", codigo="MTZ001", endereco="Av. Principal, 1000",
                cidade="São Paulo", estado="SP", cep="01310-100",
                telefone="(11) 3000-0000", email="matriz@crmconsorcio.com.br", ativo=True),
        Unidade(nome="Filial Rio de Janeiro", codigo="RJ001", endereco="Av. Rio Branco, 500",
                cidade="Rio de Janeiro", estado="RJ", cep="20040-020",
                telefone="(21) 3000-0000", email="rj@crmconsorcio.com.br", ativo=True),
        Unidade(nome="Filial Belo Horizonte", codigo="BH001", endereco="Av. Afonso Pena, 2000",
                cidade="Belo Horizonte", estado="MG", cep="30130-000",
                telefone="(31) 3000-0000", email="bh@crmconsorcio.com.br", ativo=True),
    ]
    for u in unidades:
        if not db.query(Unidade).filter(Unidade.codigo == u.codigo).first():
            db.add(u)
            print(f"Unidade criada: {u.nome}")
    db.commit()


def seed_empresas(db: Session):
    empresas = [
        Empresa(razao_social="HM Consórcios Ltda", nome_fantasia="HM Consórcios",
                cnpj="12.345.678/0001-90", endereco="Av. Principal, 1000",
                cidade="São Paulo", estado="SP", cep="01310-100",
                telefone="(11) 3000-0000", email="contato@hmconsorcios.com.br", ativo=True),
    ]
    for e in empresas:
        if not db.query(Empresa).filter(Empresa.cnpj == e.cnpj).first():
            db.add(e)
            print(f"Empresa criada: {e.razao_social}")
    db.commit()


def seed_usuarios(db: Session):
    matriz = db.query(Unidade).filter(Unidade.codigo == "MTZ001").first()

    # perfil_id: 1=admin, 2=gerente, 3=vendedor, 4=consultor
    usuarios = [
        Usuario(nome="Administrador", email="admin@crmconsorcio.com.br",
                senha_hash=get_password_hash("admin123"), perfil_id=1,
                unidade_id=matriz.id if matriz else None, ativo=True),
        Usuario(nome="Gerente Matriz", email="gerente@crmconsorcio.com.br",
                senha_hash=get_password_hash("gerente123"), perfil_id=2,
                unidade_id=matriz.id if matriz else None, ativo=True),
        Usuario(nome="Representante Teste", email="representante@crmconsorcio.com.br",
                senha_hash=get_password_hash("repr123"), perfil_id=3,
                unidade_id=matriz.id if matriz else None, ativo=True),
        Usuario(nome="Consultor Teste", email="consultor@crmconsorcio.com.br",
                senha_hash=get_password_hash("cons123"), perfil_id=4,
                unidade_id=matriz.id if matriz else None, ativo=True),
    ]
    for u in usuarios:
        if not db.query(Usuario).filter(Usuario.email == u.email).first():
            db.add(u)
            print(f"Usuário criado: {u.email}")
    db.commit()


def seed_tabelas_credito(db: Session):
    tabelas = [
        # IMÓVEIS
        TabelaCredito(nome="Imóvel 50K - 120m", tipo_bem="imovel", prazo=120,
                      valor_credito=Decimal("50000"), parcela=Decimal("450"), fundo_reserva=Decimal("2.5")),
        TabelaCredito(nome="Imóvel 75K - 120m", tipo_bem="imovel", prazo=120,
                      valor_credito=Decimal("75000"), parcela=Decimal("675"), fundo_reserva=Decimal("2.5")),
        TabelaCredito(nome="Imóvel 100K - 120m", tipo_bem="imovel", prazo=120,
                      valor_credito=Decimal("100000"), parcela=Decimal("900"), fundo_reserva=Decimal("2.5")),
        TabelaCredito(nome="Imóvel 150K - 150m", tipo_bem="imovel", prazo=150,
                      valor_credito=Decimal("150000"), parcela=Decimal("1100"), fundo_reserva=Decimal("2.5")),
        TabelaCredito(nome="Imóvel 200K - 180m", tipo_bem="imovel", prazo=180,
                      valor_credito=Decimal("200000"), parcela=Decimal("1250"), fundo_reserva=Decimal("2.5")),
        # CARROS
        TabelaCredito(nome="Carro 30K - 60m", tipo_bem="carro", prazo=60,
                      valor_credito=Decimal("30000"), parcela=Decimal("550"), fundo_reserva=Decimal("3.0")),
        TabelaCredito(nome="Carro 50K - 72m", tipo_bem="carro", prazo=72,
                      valor_credito=Decimal("50000"), parcela=Decimal("770"), fundo_reserva=Decimal("3.0")),
        TabelaCredito(nome="Carro 70K - 80m", tipo_bem="carro", prazo=80,
                      valor_credito=Decimal("70000"), parcela=Decimal("980"), fundo_reserva=Decimal("3.0")),
        # MOTOS
        TabelaCredito(nome="Moto 10K - 48m", tipo_bem="moto", prazo=48,
                      valor_credito=Decimal("10000"), parcela=Decimal("230"), fundo_reserva=Decimal("3.5")),
        TabelaCredito(nome="Moto 15K - 60m", tipo_bem="moto", prazo=60,
                      valor_credito=Decimal("15000"), parcela=Decimal("280"), fundo_reserva=Decimal("3.5")),
        TabelaCredito(nome="Moto 20K - 60m", tipo_bem="moto", prazo=60,
                      valor_credito=Decimal("20000"), parcela=Decimal("370"), fundo_reserva=Decimal("3.5")),
    ]
    for t in tabelas:
        if not db.query(TabelaCredito).filter(TabelaCredito.nome == t.nome).first():
            db.add(t)
            print(f"Tabela criada: {t.nome}")
    db.commit()


def seed_administradoras(db: Session):
    admins = [
        Administradora(nome="Consórcio Nacional", cnpj="11.111.111/0001-11",
                       endereco="Av. Paulista, 1000", cidade="São Paulo", estado="SP",
                       telefone="(11) 4000-0000", email="contato@consnacional.com.br"),
        Administradora(nome="Embracon", cnpj="22.222.222/0001-22",
                       endereco="Av. Brasil, 500", cidade="São Paulo", estado="SP",
                       telefone="(11) 4000-0001", email="contato@embracon.com.br"),
    ]
    for a in admins:
        if not db.query(Administradora).filter(Administradora.cnpj == a.cnpj).first():
            db.add(a)
            print(f"Administradora criada: {a.nome}")
    db.commit()


def main():
    print("=" * 50)
    print("Iniciando seed do banco de dados...")
    print("=" * 50)
    db = SessionLocal()
    try:
        seed_unidades(db)
        seed_empresas(db)
        seed_usuarios(db)
        seed_tabelas_credito(db)
        seed_administradoras(db)
        print("=" * 50)
        print("Seed concluído!")
        print("=" * 50)
        print("\nUsuários de teste:")
        print("  Admin: admin@crmconsorcio.com.br / admin123")
        print("  Gerente: gerente@crmconsorcio.com.br / gerente123")
        print("  Representante: representante@crmconsorcio.com.br / repr123")
    except Exception as e:
        print(f"Erro: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

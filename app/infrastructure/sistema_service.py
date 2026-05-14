import datetime
import random

from app.domain.models import Base, Produto, Cliente, Operador
from app.infrastructure.repositories.cliente_repository import SQLAlchemyClienteRepository
from app.infrastructure.repositories.compra_repository import SQLAlchemyCompraRepository
from app.infrastructure.repositories.operador_repository import SQLAlchemyOperadorRepository
from app.infrastructure.repositories.produto_repository import SQLAlchemyProdutoRepository
from app.shared.progressbar import barra_progresso
from database.connection.conexao_db import ConexaoDB
from database.data.executar_script_db import executar_script_sql
from database.data.inserir_dados_csv_no_db import inserir_dados_csv
from app.assets.estilos import (
    busca, azul, vermelho, reset,
    produtos_emoticon, clientes_emoticon,
    ok, cancela_emoticon, criando, stop_emoticon,
)


def _criar_tabelas(sessao):
    bind = sessao.get_bind()
    Base.metadata.create_all(bind)
    _aplicar_migracoes(bind)


def _aplicar_migracoes(bind):
    from sqlalchemy import inspect, text
    try:
        inspector = inspect(bind)
        if 'compra' not in inspector.get_table_names():
            return
        colunas = {c['name'] for c in inspector.get_columns('compra')}
        alteracoes = []
        if 'id_operador' not in colunas:
            alteracoes.append("ADD COLUMN id_operador INT")
        if 'token_compra' not in colunas:
            alteracoes.append("ADD COLUMN token_compra VARCHAR(36)")
        if alteracoes:
            with bind.connect() as conn:
                conn.execute(text(f"ALTER TABLE compra {', '.join(alteracoes)}"))
                conn.commit()
    except Exception:
        return


def _seed_entidade(sessao, count_fn, csv_fn, label):
    if not count_fn():
        csv_fn(sessao, label)


def _popular_se_vazio(sessao):
    import pathlib
    import csv as _csv
    diretorio_seeds = pathlib.Path(__file__).parent.parent.parent / "database" / "seeds"

    produto_repo  = SQLAlchemyProdutoRepository(sessao)
    operador_repo = SQLAlchemyOperadorRepository(sessao)
    cliente_repo  = SQLAlchemyClienteRepository(sessao)

    if not operador_repo.count():
        _seed_operadores_csv(sessao, diretorio_seeds)
    if not produto_repo.count():
        _seed_produtos_csv(sessao, diretorio_seeds)
    if not cliente_repo.count():
        _seed_clientes_csv(sessao, diretorio_seeds)
    _seed_compras_demo(sessao)


def _seed_operadores_csv(sessao, diretorio_seeds):
    import csv
    import pathlib
    from app.domain.models import Operador
    caminho = pathlib.Path(diretorio_seeds) / "operadores.csv"
    if not caminho.exists():
        return
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            for linha in csv.DictReader(f):
                sessao.add(Operador(
                    id_operador=int(linha['id']),
                    nome=linha['nome'],
                    cargo=linha['cargo'],
                    iniciais=linha['iniciais'],
                    cor=linha['cor'],
                ))
        sessao.commit()
    except Exception:
        sessao.rollback()


def _seed_produtos_csv(sessao, diretorio_seeds):
    import csv
    import pathlib
    caminho = pathlib.Path(diretorio_seeds) / "produtos.csv"
    if not caminho.exists():
        return
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            for linha in csv.DictReader(f):
                sessao.add(Produto(
                    id_produto=int(linha['id']),
                    nome=linha['nome'],
                    quantidade=int(linha['quantidade']),
                    preco=float(linha['preco']),
                ))
        sessao.commit()
    except Exception:
        sessao.rollback()


def _seed_clientes_csv(sessao, diretorio_seeds):
    import csv
    import pathlib
    caminho = pathlib.Path(diretorio_seeds) / "clientes.csv"
    if not caminho.exists():
        return
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            for linha in csv.DictReader(f):
                sessao.add(Cliente(
                    id_cliente=int(linha['id']),
                    nome=linha['nome'],
                ))
        sessao.commit()
    except Exception:
        sessao.rollback()


def _seed_compras_demo(sessao):
    from sqlalchemy import func
    from app.domain.models import Compra, Item
    try:
        count = sessao.query(func.count(Compra.id_compra)).scalar() or 0
        if count > 0:
            return
    except Exception:
        return

    hoje = datetime.date.today()
    random.seed(42)

    _CLIENTES   = [1, 2, 3, 4, 5]
    _OPERADORES = [1, 2, 3, 4, 5]
    _PRODUTOS   = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    try:
        idx = 0
        for offset in range(29, -1, -1):
            dia = hoje - datetime.timedelta(days=offset)
            if dia.weekday() == 6 and random.random() < 0.4:
                continue
            n = random.randint(4, 10)
            for _ in range(n):
                hora = random.randint(8, 20)
                minuto = random.randint(0, 59)
                dt = datetime.datetime(dia.year, dia.month, dia.day, hora, minuto)
                compra = Compra(
                    data_compra=dt,
                    id_cliente=random.choice(_CLIENTES),
                    id_operador=random.choice(_OPERADORES),
                    token_compra=f"DEMO{idx:04d}",
                )
                sessao.add(compra)
                sessao.flush()
                itens = random.sample(_PRODUTOS, random.randint(1, 4))
                for id_prod in itens:
                    sessao.add(Item(
                        id_compra=compra.id_compra,
                        id_produto=id_prod,
                        quantidade=random.randint(1, 3),
                    ))
                idx += 1
        sessao.commit()
    except Exception:
        sessao.rollback()


def _criar_banco_e_popular(conexao):
    print(f"{stop_emoticon}{vermelho} Banco não encontrado. {criando}{azul} Criando...{reset}\n")
    executar_script_sql()
    sessao = conexao.conectar_banco()
    inserir_dados_csv(sessao)
    return sessao


def inicializar_banco():
    print(f"{busca}{azul} Verificando banco de dados...{reset}\n")
    conexao = ConexaoDB()
    try:
        sessao = conexao.conectar_banco()
        if not sessao:
            return None
        _criar_tabelas(sessao)
        _popular_se_vazio(sessao)
        return sessao
    except Exception as e:
        if "Unknown database" in str(e):
            return _criar_banco_e_popular(conexao)
        print(f"{cancela_emoticon}{vermelho} Erro ao inicializar banco: {e}{reset}")
        return None


def carregar_dados_iniciais(sessao):
    produto_repo = SQLAlchemyProdutoRepository(sessao)
    cliente_repo = SQLAlchemyClienteRepository(sessao)
    operador_repo = SQLAlchemyOperadorRepository(sessao)
    list(barra_progresso(produto_repo.todos(), f"{produtos_emoticon} Carregando produtos"))
    print()
    list(barra_progresso(cliente_repo.todos(), f"{clientes_emoticon} Carregando clientes"))
    print()
    list(barra_progresso(operador_repo.todos(), f"{ok} Carregando operadores"))
    print()


def finalizar_sistema(sessao):
    try:
        sessao.commit()
    except Exception:
        sessao.rollback()
        raise
    finally:
        sessao.close()

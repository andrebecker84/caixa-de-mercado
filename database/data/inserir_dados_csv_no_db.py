import csv
import pathlib
import sys
from app.assets.estilos import *
from app.shared.progressbar import barra_progresso

diretorio_atual = pathlib.Path(__file__).parent.resolve()
diretorio_raiz = diretorio_atual.parent
sys.path.append(str(diretorio_raiz))

from database.connection.conexao_db import ConexaoDB
from app.domain.models import Produto, Cliente, Operador


def inserir_dados_csv(sessao):
    try:
        caminho_operadores = diretorio_raiz / "seeds" / "operadores.csv"
        if caminho_operadores.exists():
            with open(caminho_operadores, 'r', encoding='utf-8') as arquivo:
                linhas = list(csv.DictReader(arquivo))
                for linha in barra_progresso(linhas, f"{carregando} Inserindo operadores"):
                    sessao.add(Operador(
                        id_operador=int(linha['id']),
                        nome=linha['nome'],
                        cargo=linha['cargo'],
                        iniciais=linha['iniciais'],
                        cor=linha['cor'],
                    ))
            print()

        caminho_produtos = diretorio_raiz / "seeds" / "produtos.csv"
        with open(caminho_produtos, 'r', encoding='utf-8') as arquivo:
            linhas = list(csv.DictReader(arquivo))
            for linha in barra_progresso(linhas, f"{carregando} Inserindo produtos"):
                sessao.add(Produto(
                    id_produto=int(linha['id']),
                    nome=linha['nome'],
                    quantidade=int(linha['quantidade']),
                    preco=float(linha['preco']),
                ))
        print()

        caminho_clientes = diretorio_raiz / "seeds" / "clientes.csv"
        with open(caminho_clientes, 'r', encoding='utf-8') as arquivo:
            linhas = list(csv.DictReader(arquivo))
            for linha in barra_progresso(linhas, f"{carregando} Inserindo clientes"):
                sessao.add(Cliente(
                    id_cliente=int(linha['id']),
                    nome=linha['nome'],
                ))

        sessao.commit()
        print(f"\n{ok}{verde} Dados inseridos com sucesso!{reset}\n")
    except Exception as erro:
        sessao.rollback()
        print(f"{cancela_emoticon}{vermelho} Erro ao inserir dados: {erro}{reset}")


if __name__ == "__main__":
    db = ConexaoDB()
    session = db.conectar_banco()

    if not session:
        print(f"{cancela_emoticon}{vermelho} Erro: Falha ao conectar ao banco de dados.{reset}")
    else:
        try:
            inserir_dados_csv(session)
        finally:
            db.desconectar_banco(session)

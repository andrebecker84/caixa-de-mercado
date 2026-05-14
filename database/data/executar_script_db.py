import pathlib
import sys

from sqlalchemy import text

from app.shared.progressbar import barra_progresso

diretorio_atual = pathlib.Path(__file__).parent.resolve()
diretorio_raiz = diretorio_atual.parent.parent
sys.path.insert(0, str(diretorio_raiz))

from database.connection.conexao_db import ConexaoDB


def executar_script_sql():
    caminho_script = diretorio_atual / "criar_banco.sql"

    if not caminho_script.exists():
        print(f"Erro: '{caminho_script}' não encontrado.")
        return

    with open(caminho_script, 'r', encoding='utf-8') as arquivo:
        script_sql = arquivo.read()

    comandos = [c.strip() for c in script_sql.split(';') if c.strip()]

    db = ConexaoDB()
    sessao = db.conectar_banco(usar_banco=False)
    if not sessao:
        print("Erro: não foi possível conectar ao banco.")
        return

    try:
        for comando in barra_progresso(comandos, "Executando comandos SQL"):
            sessao.execute(text(comando))
        sessao.commit()
        print("\nScript SQL executado com sucesso!")
    except Exception as erro:
        sessao.rollback()
        print(f"\nErro ao executar script SQL: {erro}")
    finally:
        db.desconectar_banco(sessao)


if __name__ == "__main__":
    executar_script_sql()

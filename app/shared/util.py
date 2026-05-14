import os
from datetime import datetime
from app.assets.estilos import *


def entrar_inteiro(mensagem):
    while True:
        try:
            return int(input(mensagem))
        except ValueError:
            print(f"{cancela_emoticon}{vermelho} Erro: entrada inválida. Digite um número inteiro.{reset}")


def entrar_opcao(exibir_menu, opcoes_validas):
    exibir_menu()
    while True:
        opcao = entrar_inteiro(f"{input_emoticon} Escolha uma opção: ")
        if opcao in opcoes_validas:
            return opcao
        print(f"{cancela_emoticon}{vermelho} Erro: opção não existente. Tente novamente.{reset}")


def exibir_data():
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


def obter_versao():
    caminho_atual = os.path.abspath(__file__)
    caminho_principal = os.path.dirname(os.path.dirname(os.path.dirname(caminho_atual)))
    nome_pasta = os.path.basename(caminho_principal)

    partes = nome_pasta.split("_")
    for parte in partes:
        if parte.lower().startswith("v") and len(parte) > 1 and parte[1:].replace('.', '').isdigit():
            return parte
    return "versão desconhecida"

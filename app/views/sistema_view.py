from app.assets.estilos import *

def exibir_cancelamento():
    print(f"\n{cancela_emoticon}{vermelho} Operação cancelada pelo usuário.{reset}")


def exibir_erro_sistema(erro):
    print(f"\n{erro_emoticon}{vermelho} Erro Fatal do Sistema: {erro}{reset}")


def exibir_bem_vindo():
    print(f"\n{negrito}{amarelo} ============================================================{reset}")
    print(f"{negrito}{amarelo}   caixaMercado  |  Bem-vindo ao Sistema de Vendas{reset}")
    print(f"{negrito}{amarelo} ============================================================{reset}\n")

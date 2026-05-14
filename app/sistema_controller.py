from app.assets.estilos import *
from app.core.atendimento_handler import AtendimentoHandler
from app.core.fechar_caixa_handler import FecharCaixaHandler
from app.infrastructure.sistema_service import (
    inicializar_banco,
    carregar_dados_iniciais,
    finalizar_sistema,
)
from app.shared.util import entrar_opcao, limpar_tela
from app.views.sistema_view import exibir_bem_vindo, exibir_erro_sistema


def _exibir_menu() -> None:
    print(f"\n{negrito}{amarelo} ============================================================{reset}")
    print(f"{negrito}{amarelo}   caixaMercado  |  Menu Principal{reset}")
    print(f"{negrito}{amarelo} ============================================================{reset}")
    print(f"  {venda_emoticon}  [1] Novo Atendimento")
    print(f"  {caixa_emoticon}  [2] Fechar Caixa")
    print(f"  {fechar_emoticon}  [0] Sair")
    print(f"{negrito}{amarelo} ============================================================{reset}\n")


def iniciar_sistema() -> None:
    limpar_tela()
    exibir_bem_vindo()

    sessao = inicializar_banco()
    if not sessao:
        exibir_erro_sistema("Não foi possível conectar ao banco de dados.")
        return

    carregar_dados_iniciais(sessao)

    comandos = {
        1: AtendimentoHandler(sessao),
        2: FecharCaixaHandler(sessao),
    }

    try:
        while True:
            opcao = entrar_opcao(_exibir_menu, {0, 1, 2})
            if opcao == 0:
                break
            comandos[opcao].executar()
    except KeyboardInterrupt:
        pass
    finally:
        finalizar_sistema(sessao)

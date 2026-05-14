from app.core.ports import AtendimentoPort
from app.shared.util import entrar_inteiro
from app.assets.estilos import *

class AtendimentoTerminalAdapter(AtendimentoPort):
    def exibir_inicio(self, cliente_nome: str) -> None:
        print(f"\n{venda_emoticon}{amarelo} --- Atendimento Iniciado: {cliente_nome} ---{reset}")

    def exibir_produtos(self, produtos: list) -> None:
        print(f"\n{produtos_emoticon}{azul} Produtos Disponíveis:{reset}")
        for p in produtos:
            print(f"[{p.id_produto}] {p.nome} - R$ {p.preco:.2f} (Estoque: {p.quantidade})")

    def pedir_id_produto(self) -> int:
        return entrar_inteiro(f"{input_emoticon}{azul} ID do Produto (0 para finalizar): {reset}")

    def pedir_quantidade(self, nome: str) -> int:
        return entrar_inteiro(f"{input_emoticon}{azul} Quantidade de '{nome}': {reset}")

    def confirmar_adicao(self, nome: str, quantidade: int) -> bool:
        res = input(f"{input_emoticon}{amarelo} Confirmar {quantidade}x {nome}? (S/N): {reset}").lower()
        return res == 's'

    def exibir_item_adicionado(self, nome: str, carrinho: list) -> None:
        print(f"{ok}{verde} {nome} adicionado ao carrinho.{reset}")

    def exibir_item_nao_adicionado(self, nome: str) -> None:
        print(f"{cancela_emoticon}{vermelho} {nome} não adicionado.{reset}")

    def exibir_carrinho(self, cliente_nome: str, carrinho: list, cancelados: list, total: float) -> None:
        print(f"\n{venda_emoticon}{amarelo} Resumo da Compra - {cliente_nome}{reset}")
        for item in carrinho:
            print(f"- {item.quantidade}x {item.nome} (Subtotal: R$ {item.subtotal:.2f})")
        print(f"{negrito}{verde} Total: R$ {total:.2f}{reset}")

    def confirmar_compra(self) -> int:
        res = input(f"\n{input_emoticon}{amarelo} Finalizar compra? (S/N): {reset}").lower()
        return 1 if res == 's' else 0

    def exibir_compra_cancelada(self) -> None:
        print(f"{cancela_emoticon}{vermelho} Compra cancelada.{reset}")

    def exibir_compra_registrada(self, id_compra: int) -> None:
        print(f"{ok}{verde} Compra registrada com sucesso! ID: #{id_compra}{reset}")

    def exibir_erro(self, mensagem: str) -> None:
        print(f"{erro_emoticon}{vermelho} Erro: {mensagem}{reset}")

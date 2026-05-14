from app.core.ports import CaixaPort
from app.domain.models import Produto
from app.assets.estilos import *

class CaixaTerminalAdapter(CaixaPort):
    def exibir_fechamento_inicio(self) -> None:
        print(f"\n{caixa_emoticon}{amarelo} --- Fechamento de Caixa ---{reset}")

    def exibir_fechamento_compras(self, compras: list) -> None:
        total = sum(c.total for c in compras)
        print(f"\n{venda_emoticon}{azul} {len(compras)} Compras Efetuadas:{reset}")
        for c in compras:
            print(f"- Compra #{c.id_compra}: R$ {c.total:.2f}")
        print(f"\n{negrito}{verde} Total Acumulado: R$ {total:.2f}{reset}")

    def exibir_fechamento_vazio(self) -> None:
        print(f"{cancela_emoticon}{amarelo} Nenhuma compra realizada no dia.{reset}")

    def verificar_estoque(self, sem_estoque: list[Produto], disponiveis: list[Produto]) -> None:
        print(f"\n{estoque_emoticon}{azul} Status do Estoque:{reset}")
        print(f"{verde} Produtos disponíveis: {len(disponiveis)}{reset}")
        if sem_estoque:
            print(f"{vermelho} Produtos SEM estoque: {len(sem_estoque)}{reset}")
            for p in sem_estoque:
                print(f"  - {p.nome}")

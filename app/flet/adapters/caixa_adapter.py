import flet as ft
from app.core.ports import CaixaPort
from app.domain.models import Produto
from app.flet.controller import PageController
from app.flet import theme as th


class CaixaFletAdapter(CaixaPort):
    def __init__(self, ctrl: PageController):
        self._ctrl = ctrl

    def _run_sync(self, fn) -> None:
        """Schedules fn on the Flet event loop and blocks until it completes."""
        async def _async():
            fn()
        self._ctrl.page.run_task(_async).result()

    def exibir_fechamento_inicio(self) -> None:
        page = self._ctrl.page
        self._run_sync(lambda: self._ctrl.set_content(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.POINT_OF_SALE, color=th.primary(page), size=32),
                    ft.Text("Fechamento de Caixa", size=28, weight=ft.FontWeight.BOLD),
                ], spacing=15),
                ft.Divider(color=th.border(page)),
                ft.Text("Processando totais do dia...", size=16, color=th.muted(page)),
                ft.ProgressBar(width=400, color=th.primary(page)),
            ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ))

    def exibir_fechamento_compras(self, compras: list) -> None:
        page        = self._ctrl.page
        total_vendas = sum(c.total for c in compras)
        qtd_compras  = len(compras)

        rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(f"#{c.id_compra}")),
                ft.DataCell(ft.Text(c.cliente.nome if c.cliente else "N/A")),
                ft.DataCell(ft.Text(f"R$ {c.total:.2f}", weight=ft.FontWeight.W_600)),
            ])
            for c in compras
        ]

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Total")),
            ],
            rows=rows,
        )

        self._run_sync(lambda: self._ctrl.set_content(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.SUMMARIZE, color=th.success(page), size=32),
                    ft.Text("Relatório de Vendas", size=28, weight=ft.FontWeight.BOLD),
                ], spacing=15),
                ft.Divider(color=th.border(page)),
                ft.Row([
                    self._ctrl.make_card(
                        ft.Column([
                            ft.Text("Total Arrecadado", size=14, color=th.muted(page)),
                            ft.Text(f"R$ {total_vendas:.2f}", size=24,
                                    weight=ft.FontWeight.BOLD, color=th.success(page)),
                        ], spacing=5),
                        padding=20,
                    ),
                    self._ctrl.make_card(
                        ft.Column([
                            ft.Text("Quantidade de Vendas", size=14, color=th.muted(page)),
                            ft.Text(str(qtd_compras), size=24, weight=ft.FontWeight.BOLD),
                        ], spacing=5),
                        padding=20,
                    ),
                ], spacing=20),
                self._ctrl.make_card(table, padding=10),
            ], spacing=20)
        ))

    def exibir_fechamento_vazio(self) -> None:
        page = self._ctrl.page
        self._run_sync(lambda: self._ctrl.set_content(
            ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=th.muted(page)),
                ft.Text("Nenhuma venda realizada hoje.", size=18, color=th.muted(page)),
                self._ctrl.make_primary_btn("Voltar", lambda _: None),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
        ))

    def verificar_estoque(self, sem_estoque: list[Produto], disponiveis: list[Produto]) -> None:
        page = self._ctrl.page
        content = ft.Column([
            ft.Text("Status do Estoque", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Icon(ft.Icons.CANCEL, color=th.danger(page), size=16),
                ft.Text(f"Produtos sem estoque: {len(sem_estoque)}", color=th.danger(page)),
            ]),
            ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=th.success(page), size=16),
                ft.Text(f"Produtos disponíveis: {len(disponiveis)}", color=th.success(page)),
            ]),
        ], spacing=10)
        self._run_sync(lambda: self._ctrl.append_content(
            self._ctrl.make_card(content, padding=20)
        ))

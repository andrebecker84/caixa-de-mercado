import flet as ft

from app.flet.controller import PageController
from app.flet import theme as th
from app.domain.models import Operador
from app.shared.datas import agora, data_longa
from app.shared.ui_helpers import avatar_color as _palette_color, initials as _initials


_CHART_COLORS = [
    "#FF4B2B", "#FF416C", "#FFB700", "#4ECDC4", "#45B7D1",
    "#A29BFE", "#FD79A8", "#00C9A7",
]


class DashboardPage:
    def __init__(
        self,
        ctrl: PageController,
        operador: Operador,
        compra_repo,
        operador_repo,
        on_atendimento,
        on_fechar,
    ):
        self._ctrl = ctrl
        self._operador = operador
        self._repo = compra_repo
        self._operador_repo = operador_repo
        self._on_atendimento = on_atendimento
        self._on_fechar = on_fechar

    def show(self) -> None:
        vendas_hoje   = self._repo.total_do_dia()
        transacoes    = self._repo.contagem_hoje()
        vendas_semana = self._repo.total_da_semana()
        vendas_mes    = self._repo.total_do_mes()
        media         = vendas_hoje / transacoes if transacoes else 0
        dias_semana   = self._repo.vendas_por_dia(7)
        top_prods     = self._repo.top_produtos(5)
        melhor_op     = self._repo.melhor_operador_hoje()
        top_ops       = self._repo.top_operadores(5)
        top_clientes  = self._repo.top_clientes(5)
        val_estoque   = self._repo.valor_estoque()
        itens_mes     = self._repo.itens_vendidos_por_categoria_mes()
        args = (vendas_hoje, transacoes, media, vendas_semana, vendas_mes,
                dias_semana, top_prods, melhor_op, top_ops, top_clientes,
                val_estoque, itens_mes)
        async def _render_async():
            self._render(*args)
        self._ctrl.page.run_task(_render_async)

    def _render(
        self,
        vendas_hoje, transacoes, media, vendas_semana, vendas_mes,
        dias_semana, top_prods, melhor_op, top_ops, top_clientes,
        val_estoque, itens_mes,
    ) -> None:
        page = self._ctrl.page

        self._ctrl.set_content(
            ft.Column([
                self._build_welcome(page),
                ft.Container(height=20),
                self._build_stats_row(page, vendas_hoje, transacoes, media,
                                      vendas_semana, vendas_mes, val_estoque),
                ft.Container(height=20),
                ft.Row([
                    ft.Column([
                        self._build_chart(page, dias_semana),
                    ], expand=3),
                    ft.Column([
                        self._build_pie_chart(page, itens_mes),
                    ], expand=2),
                ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Container(height=16),
                ft.Row([
                    ft.Column([
                        self._build_top_operadores(page, top_ops),
                    ], expand=1),
                    ft.Column([
                        self._build_top_clientes(page, top_clientes),
                    ], expand=1),
                ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Container(height=16),
                ft.Row([
                    self._build_melhor_operador(page, melhor_op),
                    self._build_action_cards(page),
                ], spacing=20, alignment=ft.MainAxisAlignment.START,
                   vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Container(height=8),
            ], spacing=0, scroll=ft.ScrollMode.HIDDEN),
        )

    # ── Hero ──────────────────────────────────────────────────────

    @staticmethod
    def _saudacao(hora: int) -> str:
        if hora < 12:
            return "Bom dia"
        if hora < 18:
            return "Boa tarde"
        return "Boa noite"

    def _build_welcome(self, page: ft.Page) -> ft.Container:
        now  = agora()
        data = data_longa(now)
        dark = th.is_dark(page)
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(
                        f"{self._saudacao(now.hour)}, {self._operador.nome.split()[0]}!",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Text(
                        f"Gerenciando o caixa como {self._operador.cargo} · {data}",
                        size=13,
                        color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                    ),
                ], spacing=4, expand=True),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.BOLT_ROUNDED, color=ft.Colors.AMBER, size=16),
                        ft.Text("SISTEMA ONLINE", size=10, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.AMBER),
                    ], spacing=4),
                    padding=ft.Padding(left=12, top=6, right=12, bottom=6),
                    border_radius=20,
                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.AMBER),
                )
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=th.DARK_SURFACE if dark else th.LIGHT_PRIMARY,
            border_radius=th.RADIUS_CARD,
            padding=ft.Padding(left=30, top=30, right=30, bottom=30),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE) if dark else None),
        )

    # ── Stat cards ────────────────────────────────────────────────

    def _stat_card(self, page, icon, label, value, color, sub=None) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        ft.Icon(icon, size=18, color=color),
                        bgcolor=ft.Colors.with_opacity(0.12, color),
                        border_radius=8,
                        padding=8,
                    ),
                    ft.Container(expand=True),
                ]),
                ft.Container(height=10),
                ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=th.text(page)),
                ft.Text(label, size=12, color=th.muted(page)),
                ft.Text(sub, size=11, color=th.muted(page)) if sub else ft.Container(),
            ], spacing=2, tight=True),
            bgcolor=th.card(page),
            border_radius=th.RADIUS_CARD,
            shadow=th.card_shadows(th.is_dark(page)),
            padding=ft.Padding(left=18, top=18, right=18, bottom=18),
            expand=True,
        )

    def _build_stats_row(self, page, hoje, transacoes, media, semana, mes, val_estoque) -> ft.Row:
        return ft.Row([
            self._stat_card(page, ft.Icons.ATTACH_MONEY, "Vendas hoje",
                            f"R$ {hoje:,.2f}", th.success(page),
                            f"{transacoes} transações"),
            self._stat_card(page, ft.Icons.RECEIPT, "Ticket médio",
                            f"R$ {media:,.2f}", th.primary(page)),
            self._stat_card(page, ft.Icons.DATE_RANGE, "Vendas semana",
                            f"R$ {semana:,.2f}", th.accent(page)),
            self._stat_card(page, ft.Icons.CALENDAR_TODAY, "Vendas no mês",
                            f"R$ {mes:,.2f}", "#FFB700"),
            self._stat_card(page, ft.Icons.WAREHOUSE, "Valor em estoque",
                            f"R$ {val_estoque:,.2f}", "#4ECDC4"),
        ], spacing=14, vertical_alignment=ft.CrossAxisAlignment.START)

    # ── Weekly bar chart ──────────────────────────────────────────

    def _build_chart(self, page: ft.Page, dados: list[tuple]) -> ft.Container:
        if not dados:
            placeholder = ft.Column([
                ft.Icon(ft.Icons.SHOW_CHART, size=40, color=th.muted(page)),
                ft.Text("Sem dados na semana", size=13, color=th.muted(page)),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
            return self._ctrl.make_card(
                ft.Column([
                    self._section_header(page, ft.Icons.BAR_CHART, "Vendas últimos 7 dias"),
                    ft.Container(content=placeholder, alignment=ft.Alignment(0, 0), height=140),
                ], spacing=12), padding=18
            )

        max_val  = max(v for _, v in dados) or 1
        days_pt  = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        color_ok = th.primary(page)

        bars = []
        for dia, val in dados:
            pct     = val / max_val
            weekday = days_pt[dia.weekday()] if hasattr(dia, 'weekday') else "?"
            bar_h   = max(8, int(130 * pct))
            is_max  = val == max_val

            bars.append(
                ft.Column([
                    ft.Text(
                        f"R${val/1000:.1f}k" if val >= 1000 else f"R${val:.0f}",
                        size=9, color=th.muted(page), text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=4),
                    ft.Container(
                        width=34,
                        height=bar_h,
                        bgcolor=color_ok if not is_max
                                else ft.Colors.with_opacity(1.0, th.success(page)),
                        border_radius=ft.BorderRadius(top_left=5, top_right=5, bottom_left=0, bottom_right=0),
                        tooltip=f"{weekday} · R$ {val:,.2f}",
                        shadow=[ft.BoxShadow(
                            blur_radius=8,
                            color=ft.Colors.with_opacity(0.25, color_ok),
                        )] if is_max else None,
                    ),
                    ft.Container(height=4),
                    ft.Text(weekday, size=10, color=th.muted(page),
                            text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            )

        return self._ctrl.make_card(
            ft.Column([
                self._section_header(page, ft.Icons.BAR_CHART, "Vendas últimos 7 dias"),
                ft.Divider(color=th.border(page)),
                ft.Row(
                    bars,
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    height=180,
                ),
            ], spacing=12), padding=18
        )

    # ── Product mix — percentage bars ─────────────────────────────

    def _build_pie_chart(self, page: ft.Page, dados: list[tuple]) -> ft.Container:
        if not dados:
            body = ft.Column([
                ft.Icon(ft.Icons.DONUT_LARGE, size=40, color=th.muted(page)),
                ft.Text("Sem dados no mês", size=13, color=th.muted(page)),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
            return self._ctrl.make_card(
                ft.Column([
                    self._section_header(page, ft.Icons.DONUT_LARGE, "Mix de produtos (mês)"),
                    ft.Container(content=body, alignment=ft.Alignment(0, 0), height=140),
                ], spacing=12), padding=18,
            )

        total_geral = sum(q for _, q in dados) or 1
        rows = []
        for i, (nome, qtd) in enumerate(dados):
            cor  = _CHART_COLORS[i % len(_CHART_COLORS)]
            pct  = qtd / total_geral * 100
            bar_w = max(12, int(160 * qtd / total_geral))
            rows.append(ft.Column([
                ft.Row([
                    ft.Container(
                        width=10, height=10,
                        bgcolor=cor,
                        border_radius=3,
                    ),
                    ft.Text(nome, size=11, color=th.text(page), expand=True,
                            overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"{pct:.0f}%", size=10, color=cor,
                            weight=ft.FontWeight.W_600),
                    ft.Text(f"{qtd} un", size=10, color=th.muted(page)),
                ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row([
                    ft.Container(width=16),
                    ft.Container(
                        height=4, width=bar_w,
                        bgcolor=ft.Colors.with_opacity(0.5, cor),
                        border_radius=2,
                    ),
                ], spacing=6),
                ft.Container(height=3),
            ], spacing=2))

        return self._ctrl.make_card(
            ft.Column([
                self._section_header(page, ft.Icons.DONUT_LARGE, "Mix de produtos (mês)"),
                ft.Divider(color=th.border(page)),
                ft.Column(rows, spacing=0),
            ], spacing=10), padding=18,
        )

    # ── Top operadores mês ────────────────────────────────────────

    def _build_top_operadores(self, page: ft.Page, dados: list[tuple]) -> ft.Container:
        if not dados:
            body = ft.Text("Sem dados no mês", size=13, color=th.muted(page))
        else:
            max_total = max(t for _, _, t in dados) or 1
            rows = []
            for i, (id_op, qtd, total) in enumerate(dados):
                op   = self._operador_repo.buscar_por_id(id_op)
                nome = op.nome     if op else f"Operador #{id_op}"
                cor  = op.cor      if op else _CHART_COLORS[i % len(_CHART_COLORS)]
                ini  = op.iniciais if op else _initials(nome)
                bar_w = max(16, int(110 * total / max_total))
                rows.append(ft.Column([
                    ft.Row([
                        ft.Container(
                            ft.Text(ini, size=10, weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE,
                                    text_align=ft.TextAlign.CENTER),
                            bgcolor=cor,
                            border_radius=50,
                            width=30, height=30,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Text(nome, size=12, color=th.text(page), expand=True,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                weight=ft.FontWeight.W_500),
                        ft.Text(f"{qtd} vendas", size=11, color=th.muted(page)),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Row([
                        ft.Container(width=38),
                        ft.Container(
                            height=4, width=bar_w,
                            bgcolor=ft.Colors.with_opacity(0.35, cor),
                            border_radius=2,
                        ),
                        ft.Container(expand=True),
                        ft.Text(f"R$ {total:,.0f}", size=11, color=cor,
                                weight=ft.FontWeight.W_600),
                    ], spacing=6),
                    ft.Container(height=4),
                ], spacing=2))
            body = ft.Column(rows, spacing=0)

        return self._ctrl.make_card(
            ft.Column([
                self._section_header(page, ft.Icons.PEOPLE, "Top operadores (mês)"),
                ft.Divider(color=th.border(page)),
                body,
            ], spacing=12), padding=18,
        )

    # ── Top clientes mês ──────────────────────────────────────────

    def _build_top_clientes(self, page: ft.Page, dados: list[tuple]) -> ft.Container:
        if not dados:
            body = ft.Text("Sem dados no mês", size=13, color=th.muted(page))
        else:
            max_gasto = max(t for _, _, t in dados) or 1
            rows = []
            for i, (nome, qtd, total) in enumerate(dados):
                cor   = _palette_color(i + 1)
                bar_w = max(16, int(110 * total / max_gasto))
                rows.append(ft.Column([
                    ft.Row([
                        ft.Container(
                            ft.Text(_initials(nome), size=10,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE,
                                    text_align=ft.TextAlign.CENTER),
                            bgcolor=cor,
                            border_radius=50,
                            width=30, height=30,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Text(nome, size=12, color=th.text(page), expand=True,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                weight=ft.FontWeight.W_500),
                        ft.Text(f"{qtd}x", size=11, color=th.muted(page)),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Row([
                        ft.Container(width=38),
                        ft.Container(
                            height=4, width=bar_w,
                            bgcolor=ft.Colors.with_opacity(0.35, cor),
                            border_radius=2,
                        ),
                        ft.Container(expand=True),
                        ft.Text(f"R$ {total:,.0f}", size=11, color=cor,
                                weight=ft.FontWeight.W_600),
                    ], spacing=6),
                    ft.Container(height=4),
                ], spacing=2))
            body = ft.Column(rows, spacing=0)

        return self._ctrl.make_card(
            ft.Column([
                self._section_header(page, ft.Icons.PERSON_PIN, "Top clientes (mês)"),
                ft.Divider(color=th.border(page)),
                body,
            ], spacing=12), padding=18,
        )

    # ── Melhor operador ───────────────────────────────────────────

    def _build_melhor_operador(self, page: ft.Page, dado: tuple | None) -> ft.Container:
        if not dado:
            content = ft.Column([
                ft.Icon(ft.Icons.PERSON, size=36, color=th.muted(page)),
                ft.Text("Sem dados hoje", size=13, color=th.muted(page)),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
        else:
            id_op, vendas, total = dado
            op   = self._operador_repo.buscar_por_id(id_op)
            nome = op.nome     if op else f"Operador #{id_op}"
            cor  = op.cor      if op else th.primary(page)
            ini  = op.iniciais if op else "??"
            content = ft.Row([
                ft.Container(
                    ft.Text(ini, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=cor,
                    border_radius=50,
                    width=52, height=52,
                    alignment=ft.Alignment(0, 0),
                    shadow=[ft.BoxShadow(blur_radius=10,
                                        color=ft.Colors.with_opacity(0.3, cor))],
                ),
                ft.Column([
                    ft.Text(nome, size=14, weight=ft.FontWeight.BOLD, color=th.text(page)),
                    ft.Text(f"{vendas} vendas · R$ {total:,.2f}", size=12, color=th.muted(page)),
                    ft.Text("Destaque do dia", size=11, color=th.success(page),
                            weight=ft.FontWeight.W_500),
                ], spacing=2, tight=True),
            ], spacing=14, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        return self._ctrl.make_card(
            ft.Column([
                self._section_header(page, ft.Icons.EMOJI_EVENTS, "Melhor operador hoje"),
                ft.Divider(color=th.border(page)),
                content,
            ], spacing=12), padding=18
        )

    # ── Action cards ──────────────────────────────────────────────

    def _build_action_cards(self, page: ft.Page) -> ft.Row:
        return ft.Row([
            self._action_card(
                page,
                icon=ft.Icons.SHOPPING_CART,
                title="Novo Atendimento",
                subtitle="Registrar compras para um cliente",
                color=th.primary(page),
                on_click=lambda e: self._on_atendimento(),
            ),
            self._action_card(
                page,
                icon=ft.Icons.POINT_OF_SALE,
                title="Fechar Caixa",
                subtitle="Encerrar o dia e gerar relatório",
                color="#FF6B6B",
                on_click=lambda e: self._on_fechar(),
            ),
        ], spacing=14)

    def _action_card(self, page, icon, title, subtitle, color, on_click) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    ft.Icon(icon, size=28, color=color),
                    bgcolor=ft.Colors.with_opacity(0.12, color),
                    border_radius=12,
                    padding=12,
                    width=54, height=54,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(height=10),
                ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=th.text(page)),
                ft.Text(subtitle, size=11, color=th.muted(page)),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.START),
            bgcolor=th.card(page),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.25, color)),
            border_radius=th.RADIUS_CARD,
            shadow=th.card_shadows(th.is_dark(page)),
            padding=ft.Padding(left=20, top=18, right=20, bottom=18),
            width=210,
            ink=True,
            ink_color=ft.Colors.with_opacity(0.07, color),
            on_click=on_click,
        )

    # ── Helper ────────────────────────────────────────────────────

    def _section_header(self, page, icon, label: str) -> ft.Row:
        return ft.Row([
            ft.Container(
                ft.Icon(icon, size=14, color=th.primary(page)),
                bgcolor=ft.Colors.with_opacity(0.10, th.primary(page)),
                border_radius=6, padding=6,
            ),
            ft.Text(label, size=13, weight=ft.FontWeight.BOLD, color=th.text(page)),
        ], spacing=8)

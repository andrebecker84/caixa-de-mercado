import calendar
import datetime

import flet as ft

from app.flet.controller import PageController
from app.flet import theme as th
from app.shared.datas import agora, nome_mes
from app.shared.ui_helpers import avatar_color as _palette_color, initials as _initials


class RelatoriosPage:

    def __init__(self, ctrl: PageController, compra_repo, operador_repo):
        self._ctrl = ctrl
        self._repo = compra_repo
        self._operador_repo = operador_repo

    def show(self) -> None:
        now       = agora()
        hoje      = self._repo.total_do_dia()
        transac   = self._repo.contagem_hoje()
        semana    = self._repo.total_da_semana()
        mes       = self._repo.total_do_mes()
        media     = hoje / transac if transac else 0
        top       = self._repo.top_produtos(10)
        cal_dados = self._repo.vendas_calendario_mes(now.year, now.month)
        async def _render_async():
            self._render(now, hoje, transac, media, semana, mes, top, cal_dados)
        self._ctrl.page.run_task(_render_async)

    def _render(self, now, hoje, transac, media, semana, mes, top, cal_dados) -> None:
        page = self._ctrl.page
        self._ctrl.set_content(
            ft.Column([
                self._build_header(page, now),
                ft.Container(height=4),
                self._build_kpis(page, hoje, transac, media, semana, mes),
                ft.Container(height=16),
                ft.Row([
                    ft.Column([
                        self._build_calendario(page, cal_dados, now.year, now.month),
                    ], expand=3),
                    ft.Column([
                        self._build_top_produtos(page, top),
                    ], expand=2),
                ], spacing=16,
                   vertical_alignment=ft.CrossAxisAlignment.START),
            ], spacing=0),
        )

    # ── Header ────────────────────────────────────────────────────

    def _build_header(self, page: ft.Page, now: datetime.datetime) -> ft.Row:
        data = now.strftime("%d/%m/%Y")
        return ft.Row([
            ft.Container(
                ft.Icon(ft.Icons.BAR_CHART, size=16, color=th.primary(page)),
                bgcolor=ft.Colors.with_opacity(0.12, th.primary(page)),
                border_radius=8, padding=8,
            ),
            ft.Column([
                ft.Text("Relatórios", size=20, weight=ft.FontWeight.BOLD,
                        color=th.text(page)),
                ft.Text(f"Dados atualizados em {data}",
                        size=12, color=th.muted(page)),
            ], spacing=2, tight=True),
        ], spacing=12)

    # ── KPI cards ─────────────────────────────────────────────────

    def _build_kpis(self, page, hoje, transac, media, semana, mes) -> ft.Row:
        def kpi(icon, label, value, color, sub=None):
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            ft.Icon(icon, size=16, color=color),
                            bgcolor=ft.Colors.with_opacity(0.12, color),
                            border_radius=8, padding=7,
                        ),
                    ]),
                    ft.Container(height=8),
                    ft.Text(value, size=20, weight=ft.FontWeight.BOLD,
                            color=th.text(page)),
                    ft.Text(label, size=11, color=th.muted(page)),
                    ft.Text(sub, size=10, color=th.muted(page)) if sub
                    else ft.Container(),
                ], spacing=2, tight=True),
                bgcolor=th.card(page),
                border_radius=ft.border_radius.all(th.RADIUS_CARD),
                shadow=th.card_shadows(th.is_dark(page)),
                padding=ft.padding.all(16),
                expand=True,
            )

        return ft.Row([
            kpi(ft.Icons.ATTACH_MONEY, "Vendas hoje",
                f"R$ {hoje:,.2f}", th.success(page),
                f"{transac} transações"),
            kpi(ft.Icons.RECEIPT,     "Ticket médio",
                f"R$ {media:,.2f}", th.primary(page)),
            kpi(ft.Icons.DATE_RANGE,  "Vendas semana",
                f"R$ {semana:,.2f}", th.accent(page)),
            kpi(ft.Icons.CALENDAR_TODAY, "Vendas no mês",
                f"R$ {mes:,.2f}", "#FFB700"),
        ], spacing=14, vertical_alignment=ft.CrossAxisAlignment.STRETCH)

    # ── Monthly calendar ──────────────────────────────────────────

    def _build_calendario(self, page: ft.Page, dados: dict,
                          ano: int, mes: int) -> ft.Container:
        DIAS_SEMANA = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        hoje = agora().date()

        section = self._section_header(
            page, ft.Icons.CALENDAR_MONTH,
            f"Calendário — {nome_mes(mes)} {ano}",
        )

        headers = ft.Row([
            ft.Container(
                ft.Text(d, size=10, color=th.muted(page),
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.W_500),
                expand=True,
            )
            for d in DIAS_SEMANA
        ], spacing=3)

        semanas = calendar.monthcalendar(ano, mes)
        linhas  = []
        for semana in semanas:
            celulas = []
            for dia in semana:
                if dia == 0:
                    celulas.append(ft.Container(expand=True))
                    continue
                info   = dados.get(dia, {})
                total  = info.get('total', 0)
                trans  = info.get('transacoes', 0)
                vendas = total > 0
                is_hoje = datetime.date(ano, mes, dia) == hoje

                cor_dia = th.primary(page) if is_hoje else th.text(page)

                valor_txt = (
                    ft.Text(
                        f"R${total/1000:.1f}k" if total >= 1000 else f"R${total:.0f}",
                        size=8, color=th.primary(page),
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.W_500,
                    )
                    if vendas else ft.Container(height=11)
                )
                trans_txt = (
                    ft.Text(
                        f"{trans}x", size=7, color=th.muted(page),
                        text_align=ft.TextAlign.CENTER,
                    )
                    if vendas else ft.Container(height=9)
                )

                def _make_click(d=dia, info_d=info, has_data=vendas):
                    return (lambda e: self._on_dia_click(d, info_d, ano, mes)) if has_data else None

                celula = ft.Container(
                    content=ft.Column([
                        ft.Text(str(dia), size=11,
                                weight=ft.FontWeight.BOLD if is_hoje else ft.FontWeight.NORMAL,
                                color=cor_dia,
                                text_align=ft.TextAlign.CENTER),
                        ft.Container(
                            height=3,
                            bgcolor=th.success(page) if vendas else ft.Colors.TRANSPARENT,
                            border_radius=2,
                        ),
                        valor_txt,
                        trans_txt,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                       spacing=1, tight=True),
                    expand=True,
                    border=ft.border.all(
                        1.5 if is_hoje else 1,
                        th.primary(page) if is_hoje
                        else (ft.Colors.with_opacity(0.25, th.success(page)) if vendas
                              else th.border(page)),
                    ),
                    border_radius=6,
                    padding=ft.padding.symmetric(horizontal=2, vertical=5),
                    bgcolor=(
                        ft.Colors.with_opacity(0.10, th.primary(page)) if is_hoje
                        else ft.Colors.with_opacity(0.04, th.success(page)) if vendas
                        else ft.Colors.TRANSPARENT
                    ),
                    tooltip=f"{trans} transações · R$ {total:,.2f}" if vendas else None,
                    ink=vendas,
                    ink_color=ft.Colors.with_opacity(0.06, th.primary(page)) if vendas else None,
                    on_click=_make_click(),
                )
                celulas.append(celula)
            linhas.append(ft.Row(celulas, spacing=3))

        return self._ctrl.make_card(
            ft.Column([
                section,
                ft.Divider(color=th.border(page)),
                headers,
                ft.Container(height=4),
                ft.Column(linhas, spacing=3),
            ], spacing=8),
            padding=18,
        )

    def _on_dia_click(self, dia: int, info: dict, ano: int, mes: int) -> None:
        page  = self._ctrl.page
        total = info.get('total', 0)
        trans = info.get('transacoes', 0)
        ops   = self._repo.vendas_por_operador_no_dia(ano, mes, dia)

        data_fmt = f"{dia:02d}/{mes:02d}/{ano}"

        if ops:
            op_rows = []
            for id_op, qtd, subtotal in ops:
                op  = self._operador_repo.buscar_por_id(id_op)
                nome = op.nome     if op else f"Operador #{id_op}"
                cor  = op.cor      if op else th.primary(page)
                ini  = op.iniciais if op else _initials(nome)
                op_rows.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                ft.Text(ini, size=11, weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE,
                                        text_align=ft.TextAlign.CENTER),
                                bgcolor=cor,
                                border_radius=ft.border_radius.all(50),
                                width=34, height=34,
                                alignment=ft.Alignment(0, 0),
                                shadow=[ft.BoxShadow(blur_radius=6,
                                                    color=ft.Colors.with_opacity(0.25, cor))],
                            ),
                            ft.Column([
                                ft.Text(nome, size=12, weight=ft.FontWeight.W_600,
                                        color=th.text(page),
                                        overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text(f"{qtd} venda{'s' if qtd != 1 else ''}",
                                        size=10, color=th.muted(page)),
                            ], spacing=2, tight=True, expand=True),
                            ft.Text(f"R$ {subtotal:,.2f}", size=12,
                                    color=cor, weight=ft.FontWeight.BOLD),
                        ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=ft.Colors.with_opacity(0.04, cor),
                        border=ft.border.all(1, ft.Colors.with_opacity(0.18, cor)),
                        border_radius=10,
                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        margin=ft.margin.only(bottom=6),
                    )
                )
            detail_body = ft.Column(op_rows, spacing=0)
        else:
            detail_body = ft.Column([
                ft.Icon(ft.Icons.PERSON_OFF, size=32, color=th.muted(page)),
                ft.Text("Sem detalhes por operador", size=13, color=th.muted(page)),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Container(
                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color=th.primary(page)),
                    bgcolor=ft.Colors.with_opacity(0.12, th.primary(page)),
                    border_radius=6, padding=6,
                ),
                ft.Column([
                    ft.Text(f"Vendas em {data_fmt}", size=14,
                            weight=ft.FontWeight.BOLD, color=th.text(page)),
                    ft.Text(f"{trans} transação{'ões' if trans != 1 else ''} · R$ {total:,.2f}",
                            size=11, color=th.muted(page)),
                ], spacing=1, tight=True),
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            content=ft.Container(
                content=detail_body,
                width=380,
                padding=ft.padding.symmetric(vertical=4),
            ),
            actions=[
                ft.TextButton(
                    "Fechar",
                    on_click=lambda e: self._ctrl.close_dialog(),
                    style=ft.ButtonStyle(color=th.primary(page)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=th.card(page),
            shape=ft.RoundedRectangleBorder(radius=th.RADIUS_CARD),
        )
        self._ctrl.show_dialog(dialog)

    # ── Top produtos ──────────────────────────────────────────────

    def _build_top_produtos(self, page: ft.Page, dados: list) -> ft.Container:
        section = self._section_header(page, ft.Icons.STAR,
                                       "Top 10 produtos (mês)")
        if not dados:
            body = ft.Text("Sem dados no período", size=13,
                           color=th.muted(page))
        else:
            colors  = [th.primary(page), th.accent(page), "#FFB700",
                       "#FF6B6B", "#4ECDC4", "#45B7D1", "#A29BFE",
                       "#FD79A8", "#00C9A7", "#FFB700"]
            max_qtd = max(q for _, q, _ in dados) or 1
            rows    = []
            for i, (nome, qtd, total) in enumerate(dados):
                color = colors[i % len(colors)]
                bar_w = max(16, int(100 * qtd / max_qtd))
                rows.append(ft.Column([
                    ft.Row([
                        ft.Container(
                            ft.Text(str(i + 1), size=10,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD),
                            bgcolor=color, border_radius=4,
                            padding=ft.padding.symmetric(
                                horizontal=5, vertical=2),
                            width=22,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Text(nome, size=12, color=th.text(page),
                                expand=True,
                                overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"{qtd} un", size=11,
                                color=th.muted(page)),
                    ], spacing=6,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Row([
                        ft.Container(width=28),
                        ft.Container(
                            height=3, width=bar_w,
                            bgcolor=ft.Colors.with_opacity(0.35, color),
                            border_radius=2,
                        ),
                        ft.Container(expand=True),
                        ft.Text(f"R$ {total:.0f}", size=11, color=color,
                                weight=ft.FontWeight.W_600),
                    ], spacing=6),
                    ft.Container(height=4),
                ], spacing=2))
            body = ft.Column(rows, spacing=0)

        return self._ctrl.make_card(
            ft.Column([section, ft.Divider(color=th.border(page)), body],
                      spacing=12),
            padding=18,
        )

    # ── Helper ────────────────────────────────────────────────────

    def _section_header(self, page, icon, label: str) -> ft.Row:
        return ft.Row([
            ft.Container(
                ft.Icon(icon, size=13, color=th.primary(page)),
                bgcolor=ft.Colors.with_opacity(0.10, th.primary(page)),
                border_radius=6, padding=6,
            ),
            ft.Text(label, size=13, weight=ft.FontWeight.BOLD,
                    color=th.text(page)),
        ], spacing=8)

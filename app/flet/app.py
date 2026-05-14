import time
import uuid
import threading
import datetime

import flet as ft

from app.core.atendimento_use_case import AtendimentoUseCase
from app.core.caixa_use_case import CaixaUseCase
from app.domain.models import Operador
from app.flet import theme as th
from app.flet.adapters.atendimento_adapter import AtendimentoFletAdapter
from app.flet.adapters.caixa_adapter import CaixaFletAdapter
from app.flet.controller import PageController, ui_call
from app.flet.pages.cadastros import CadastrosPage
from app.flet.pages.dashboard import DashboardPage
from app.flet.pages.estoque import EstoquePage
from app.flet.pages.login import LoginPage
from app.flet.pages.relatorios import RelatoriosPage
from app.flet.pages.splash import SplashPage
from app.shared.ui_helpers import avatar_color as _avatar_color
from app.infrastructure.repositories.cliente_repository import SQLAlchemyClienteRepository
from app.infrastructure.repositories.compra_repository import SQLAlchemyCompraRepository
from app.infrastructure.repositories.operador_repository import SQLAlchemyOperadorRepository
from app.infrastructure.repositories.produto_repository import SQLAlchemyProdutoRepository


def main(page: ft.Page) -> None:
    page.title    = "Caixa Supermercado"
    page.theme_mode   = ft.ThemeMode.DARK
    page.window.width     = 1300
    page.window.height    = 820
    page.window.min_width = 980
    page.window.min_height = 640
    page.bgcolor  = th.DARK_BG
    page.padding  = 0
    page.fonts    = {}

    page.theme      = ft.Theme(color_scheme_seed="#FF4D00")
    page.dark_theme = ft.Theme(color_scheme_seed="#FF4D00")

    _sessao:   object   = None
    _operador: Operador | None = None

    # ── Notification history ─────────────────────────────────────
    _notif_history: list[dict] = []
    _notif_unread  = [0]
    _nav_icons: list[ft.Icon]  = []

    # ── Content body ──────────────────────────────────────────────
    body = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=16)

    # ── Sidebar nav ───────────────────────────────────────────────
    def _on_menu(e):        show_dashboard()
    def _on_atendimento(e): run_atendimento()
    def _on_fechar(e):      _confirm_fechar()
    def _on_estoque(e):     show_estoque()
    def _on_relatorio(e):   show_relatorios()
    def _on_cadastros(e):   show_cadastros()
    def _on_config(e):      _show_placeholder("Configurações", ft.Icons.SETTINGS)

    _logo_img = ft.Image(src="/logoIcon.svg", width=38, height=38, fit="contain")
    _logo_container = ft.Container(
        content=_logo_img,
        width=54, height=54,
        border_radius=14,
        bgcolor=ft.Colors.with_opacity(0.12, th.primary(page)),
        alignment=ft.Alignment(0, 0),
        margin=ft.Margin(bottom=32),
    )

    def _make_nav_btn(icon: str, label: str, on_click, active: bool = False) -> ft.Container:
        color = th.primary(page) if active else th.muted(page)
        ico = ft.Icon(icon, size=24, color=color)
        _nav_icons.append(ico)
        return ft.Container(
            content=ico,
            padding=ft.Padding(left=12, top=12, right=12, bottom=12),
            border_radius=16,
            ink=True,
            on_click=on_click,
            tooltip=label,
            alignment=ft.Alignment(0, 0),
            bgcolor=ft.Colors.with_opacity(0.1, th.primary(page)) if active else None,
        )

    nav_dashboard   = _make_nav_btn(ft.Icons.GRID_VIEW_ROUNDED,    "Dashboard",        _on_menu, active=True)
    nav_atendimento = _make_nav_btn(ft.Icons.SHOPPING_BAG_ROUNDED, "Venda",            _on_atendimento)
    nav_relatorio   = _make_nav_btn(ft.Icons.BAR_CHART_ROUNDED,    "Relatórios",       _on_relatorio)
    nav_estoque     = _make_nav_btn(ft.Icons.INVENTORY_ROUNDED,    "Estoque",          _on_estoque)
    nav_cadastros   = _make_nav_btn(ft.Icons.PEOPLE_ROUNDED,       "Cadastros",        _on_cadastros)
    nav_config      = _make_nav_btn(ft.Icons.SETTINGS_ROUNDED,     "Configurações",    _on_config)

    sidebar = ft.Container(
        content=ft.Column([
            _logo_container,
            ft.Column([
                nav_dashboard,
                nav_atendimento,
                nav_relatorio,
                nav_estoque,
                nav_cadastros,
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(expand=True),
            nav_config,
            ft.Container(height=10),
        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        width=80, # Slim sidebar like in the image
        bgcolor=th.surface(page),
        padding=ft.Padding(top=30, bottom=20),
    )

    # ── Top navbar ────────────────────────────────────────────────
    _op_iniciais = ft.Text("", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    _op_avatar_icon = ft.Icon(ft.Icons.PERSON, size=18, color=ft.Colors.WHITE)
    _op_avatar   = ft.Container(
        _op_avatar_icon,
        bgcolor=th.muted(page),
        border_radius=50,
        width=36, height=36,
        alignment=ft.Alignment(0, 0),
    )
    _op_nome  = ft.Text("", size=14, weight=ft.FontWeight.W_600, color=th.text(page))
    _op_cargo = ft.Text("", size=11, color=th.muted(page))
    _clock_time = ft.Text("", size=13, weight=ft.FontWeight.W_500, color=th.text(page))
    _clock_date = ft.Text("", size=10, color=th.muted(page))
    _clock = ft.Column(
        [_clock_time, _clock_date],
        spacing=0, tight=True,
        horizontal_alignment=ft.CrossAxisAlignment.END,
    )

    def _logout(e):
        nonlocal _operador
        _operador = None
        _update_navbar_operator()
        show_login()

    _logout_btn = ft.IconButton(
        icon=ft.Icons.LOGOUT,
        icon_color=th.muted(page),
        icon_size=17,
        tooltip="Sair",
        on_click=_logout,
    )
    _theme_btn = ft.IconButton(
        icon=ft.Icons.DARK_MODE if th.is_dark(page) else ft.Icons.LIGHT_MODE,
        icon_color=th.muted(page),
        icon_size=17,
        tooltip="Alternar Tema",
        on_click=lambda e: _toggle_theme(e),
    )

    # ── Notification bell ─────────────────────────────────────────
    _bell_badge_text = ft.Text(
        "", size=8, color=ft.Colors.WHITE,
        weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,
    )
    _bell_badge = ft.Container(
        content=_bell_badge_text,
        bgcolor=th.DARK_PRIMARY,
        border_radius=8,
        width=16, height=16,
        alignment=ft.Alignment(0, 0),
        visible=False,
        right=0, top=2,
    )
    _bell_btn = ft.IconButton(
        icon=ft.Icons.NOTIFICATIONS_NONE,
        icon_color=th.muted(page),
        icon_size=17,
        tooltip="Notificações",
        on_click=lambda e: _show_notif_history(),
    )
    _bell_stack = ft.Stack([_bell_btn, _bell_badge], width=38, height=38)

    _search_bar = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.SEARCH, color=th.muted(page), size=20),
            ft.TextField(
                hint_text="Buscar produtos, clientes...",
                border=ft.InputBorder.NONE,
                text_size=14,
                expand=True,
                hint_style=ft.TextStyle(color=th.muted(page)),
                color=th.text(page),
            )
        ], spacing=10),
        bgcolor=ft.Colors.with_opacity(0.05, th.text(page)),
        border_radius=30,
        padding=ft.Padding(left=20, top=0, right=20, bottom=0),
        width=400,
        height=45,
    )

    _right_controls = ft.Row([
        _clock,
        ft.VerticalDivider(width=1, color=th.border(page)),
        _op_avatar,
        ft.Column([_op_nome, _op_cargo], spacing=0, tight=True),
        ft.VerticalDivider(width=1, color=th.border(page)),
        _bell_stack,
        _theme_btn,
        _logout_btn,
    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    navbar = ft.Container(
        content=ft.Row([
            ft.Container(expand=True),
            _search_bar,
            ft.Container(
                content=_right_controls,
                expand=True,
                alignment=ft.Alignment(1, 0),
            ),
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=ft.Colors.TRANSPARENT,
        padding=ft.Padding(left=30, top=15, right=30, bottom=15),
        height=80,
    )

    # ── Footer ────────────────────────────────────────────────────
    _status_icon  = ft.Icon(ft.Icons.ELECTRICAL_SERVICES, size=13, color=th.danger(page))
    _status_label = ft.Text("Offline", size=10, color=th.danger(page))

    def _set_status(online: bool) -> None:
        color = th.success(page) if online else th.danger(page)
        label = "Online" if online else "Offline"
        _status_icon.color  = color
        _status_label.value = label
        _status_label.color = color
        try:
            _status_icon.update()
            _status_label.update()
        except Exception:
            pass

    footer = ft.Container(
        content=ft.Row([
            ft.Text(
                "André Luis Becker · caixaMercado · 2026",
                size=10, color=th.muted(page),
            ),
            ft.Row([
                ft.Text("v2.5", size=10, color=th.muted(page)),
                ft.Container(width=12),
                _status_icon,
                _status_label,
            ], spacing=4),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor=th.surface(page),
        border=ft.Border(top=ft.BorderSide(1, th.border(page))),
        padding=ft.Padding(left=20, top=7, right=20, bottom=7),
    )

    # ── Theme toggle ──────────────────────────────────────────────
    def _toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK
            else ft.ThemeMode.DARK
        )
        dark = th.is_dark(page)

        page.bgcolor     = th.bg(page)
        content_area.bgcolor = th.bg(page)
        sidebar.bgcolor  = th.surface(page)
        navbar.bgcolor   = ft.Colors.TRANSPARENT
        footer.bgcolor   = th.surface(page)
        footer.border    = ft.Border(top=ft.BorderSide(1, th.border(page)))

        _op_nome.color    = th.text(page)
        _op_cargo.color   = th.muted(page)
        _clock_time.color = th.text(page)
        _clock_date.color = th.muted(page)
        _search_bar.bgcolor = ft.Colors.with_opacity(0.05, th.text(page))

        _theme_btn.icon       = ft.Icons.DARK_MODE if dark else ft.Icons.LIGHT_MODE
        _theme_btn.icon_color = th.muted(page)
        _logout_btn.icon_color = th.muted(page)
        _bell_btn.icon_color   = th.muted(page)

        for ico in _nav_icons:
            ico.color = th.muted(page)

        if _sessao and _operador:
            show_dashboard()
        elif _sessao:
            show_login()

    # ── Clock updater ─────────────────────────────────────────────
    def _start_clock():
        from app.shared.datas import agora
        def _tick():
            while True:
                try:
                    now = agora()
                    def _apply(now=now):
                        _clock_time.value = now.strftime("%H:%M:%S")
                        _clock_date.value = now.strftime("%d/%m/%Y")
                        _clock_time.update()
                        _clock_date.update()
                    ui_call(page, _apply)
                except Exception:
                    break
                time.sleep(1)
        threading.Thread(target=_tick, daemon=True).start()

    # ── Operator navbar update ─────────────────────────────────────
    def _update_navbar_operator():
        if _operador:
            _op_iniciais.value    = _operador.iniciais
            _op_avatar.content    = _op_iniciais
            _op_avatar.bgcolor    = _operador.cor
            _op_nome.value        = _operador.nome
            _op_cargo.value       = _operador.cargo
        else:
            _op_avatar.content    = _op_avatar_icon
            _op_avatar.bgcolor    = th.muted(page)
            _op_nome.value        = ""
            _op_cargo.value       = ""

    # ── Infra helpers ─────────────────────────────────────────────
    def _repos():
        return (
            SQLAlchemyClienteRepository(_sessao),
            SQLAlchemyProdutoRepository(_sessao),
            SQLAlchemyCompraRepository(_sessao),
            SQLAlchemyOperadorRepository(_sessao),
        )

    ctrl = PageController(page, body)

    # ── Patch ctrl.notify to log notification history ─────────────
    _orig_notify = ctrl.notify

    def _patched_notify(message: str, ok: bool = True):
        _notif_history.append({
            'msg': message,
            'ok': ok,
            'time': datetime.datetime.now().strftime("%H:%M:%S"),
        })
        if len(_notif_history) > 50:
            _notif_history.pop(0)
        _notif_unread[0] += 1
        _bell_badge_text.value = str(_notif_unread[0]) if _notif_unread[0] < 100 else "99+"
        _bell_badge.visible = True
        _orig_notify(message, ok)

    ctrl.notify = _patched_notify

    # ── Notification history dialog ───────────────────────────────
    def _show_notif_history():
        _notif_unread[0] = 0
        _bell_badge.visible = False

        if not _notif_history:
            dialog = ft.AlertDialog(
                modal=False,
                title=ft.Row([
                    ft.Icon(ft.Icons.NOTIFICATIONS, color=th.primary(page), size=18),
                    ft.Text("Notificações", size=16, weight=ft.FontWeight.BOLD,
                            color=th.text(page)),
                ], spacing=8),
                content=ft.Container(
                    ft.Column([
                        ft.Icon(ft.Icons.NOTIFICATIONS_NONE, size=36,
                                color=th.muted(page)),
                        ft.Text("Nenhuma notificação ainda.",
                                size=13, color=th.muted(page)),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                       spacing=8),
                    padding=ft.Padding(left=20, top=20, right=20, bottom=20),
                    width=400,
                ),
                actions=[
                    ft.TextButton("Fechar", on_click=lambda e: ctrl.close_dialog(),
                                  style=ft.ButtonStyle(color=th.muted(page))),
                ],
                bgcolor=th.surface(page),
                shape=ft.RoundedRectangleBorder(radius=th.RADIUS_CARD),
            )
            ctrl.show_dialog(dialog)
            return

        rows = []
        for n in reversed(_notif_history[-30:]):
            icon  = ft.Icons.CHECK_CIRCLE if n['ok'] else ft.Icons.ERROR_OUTLINE
            color = th.success(page) if n['ok'] else th.danger(page)
            rows.append(ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, size=13, color=color),
                        ft.Text(n['time'], size=10, color=th.muted(page)),
                    ], spacing=6),
                    ft.Text(
                        n['msg'],
                        size=12,
                        color=th.text(page),
                        selectable=True,
                        no_wrap=False,
                    ),
                ], spacing=4, tight=True),
                padding=ft.Padding(left=10, top=8, right=10, bottom=8),
                border_radius=6,
                bgcolor=ft.Colors.with_opacity(
                    0.06, th.success(page) if n['ok'] else th.danger(page)
                ),
            ))

        dialog = ft.AlertDialog(
            modal=False,
            title=ft.Row([
                ft.Icon(ft.Icons.NOTIFICATIONS, color=th.primary(page), size=18),
                ft.Text("Notificações", size=16, weight=ft.FontWeight.BOLD,
                        color=th.text(page)),
                ft.Container(expand=True),
                ft.Text(f"{len(_notif_history)} total", size=11,
                        color=th.muted(page)),
            ], spacing=8),
            content=ft.Container(
                ft.Column(rows, spacing=6, scroll=ft.ScrollMode.ADAPTIVE),
                height=460,
                width=540,
                padding=ft.Padding(top=4, bottom=4),
            ),
            actions=[
                ft.TextButton("Fechar", on_click=lambda e: ctrl.close_dialog(),
                              style=ft.ButtonStyle(color=th.muted(page))),
            ],
            bgcolor=th.surface(page),
            shape=ft.RoundedRectangleBorder(radius=th.RADIUS_CARD),
        )
        ctrl.show_dialog(dialog)

    # ── Navigation ────────────────────────────────────────────────

    def show_login():
        operadores = []
        if _sessao:
            try:
                operadores = SQLAlchemyOperadorRepository(_sessao).todos()
            except RuntimeError:
                operadores = []
        LoginPage(ctrl, operadores, on_login=_on_operator_selected).show()

    def _on_operator_selected(op: Operador):
        nonlocal _operador
        _operador = op
        _update_navbar_operator()
        page.update()
        try:
            show_dashboard()
        except Exception as ex:
            ctrl.notify(f"Erro ao abrir dashboard: {ex}", ok=False)

    def show_dashboard():
        if not _sessao:
            return
        op_id = _operador.id_operador if _operador else None
        color = th.primary(page)
        ctrl.set_content(
            ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=32, height=32, stroke_width=3, color=color),
                    ft.Text("Carregando dashboard...", size=13, color=th.muted(page)),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14),
                alignment=ft.Alignment(0, 0),
                expand=True,
            )
        )

        def _load():
            try:
                _, _, compra_repo, operador_repo = _repos()
                op = operador_repo.buscar_por_id(op_id) if op_id else None
                if op is None:
                    op = _dummy_operator()
                DashboardPage(
                    ctrl, op,
                    compra_repo,
                    operador_repo,
                    on_atendimento=run_atendimento,
                    on_fechar=_confirm_fechar,
                ).show()
            except Exception as ex:
                ui_call(page, lambda: ctrl.notify(f"Erro ao carregar dashboard: {ex}", ok=False))

        threading.Thread(target=_load, daemon=True).start()

    def _dummy_operator() -> Operador:
        try:
            operadores = SQLAlchemyOperadorRepository(_sessao).todos()
            if operadores:
                return operadores[0]
        except RuntimeError:
            pass
        return Operador(nome="Sistema", cargo="", iniciais="SY", cor="#7C6FCD")

    def show_estoque():
        if not _sessao:
            return
        color = th.primary(page)
        ctrl.set_content(
            ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=32, height=32, stroke_width=3, color=color),
                    ft.Text("Carregando estoque...", size=13, color=th.muted(page)),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14),
                alignment=ft.Alignment(0, 0),
                expand=True,
            )
        )
        def _load():
            try:
                _, produto_repo, _, _ = _repos()
                EstoquePage(ctrl, produto_repo).show()
            except Exception as ex:
                ui_call(page, lambda: ctrl.notify(f"Erro ao carregar estoque: {ex}", ok=False))
        threading.Thread(target=_load, daemon=True).start()

    def show_relatorios():
        if not _sessao:
            return
        color = th.primary(page)
        ctrl.set_content(
            ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=32, height=32, stroke_width=3, color=color),
                    ft.Text("Carregando relatórios...", size=13, color=th.muted(page)),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14),
                alignment=ft.Alignment(0, 0),
                expand=True,
            )
        )
        def _load():
            try:
                _, _, compra_repo, operador_repo = _repos()
                RelatoriosPage(ctrl, compra_repo, operador_repo).show()
            except Exception as ex:
                ui_call(page, lambda: ctrl.notify(f"Erro ao carregar relatórios: {ex}", ok=False))
        threading.Thread(target=_load, daemon=True).start()

    def show_cadastros():
        if not _sessao:
            return
        def _load():
            try:
                cliente_repo, produto_repo, _, operador_repo = _repos()
                CadastrosPage(ctrl, produto_repo, cliente_repo, operador_repo).show()
            except Exception as ex:
                ui_call(page, lambda: ctrl.notify(f"Erro ao carregar cadastros: {ex}", ok=False))
        threading.Thread(target=_load, daemon=True).start()

    def _show_placeholder(titulo: str, icon: str) -> None:
        ctrl.set_content(
            ctrl.make_card(
                ft.Column([
                    ft.Icon(icon, size=52, color=th.muted(page)),
                    ctrl.make_label(titulo, size=22, bold=True),
                    ctrl.make_muted("Em desenvolvimento — disponível em breve."),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14),
                padding=60,
            )
        )

    def _confirm_fechar():
        def _yes(e):
            ctrl.close_dialog()
            run_fechar()

        def _no(e):
            ctrl.close_dialog()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.POINT_OF_SALE, color=th.danger(page), size=20),
                ft.Text("Fechar Caixa", size=16, weight=ft.FontWeight.BOLD,
                        color=th.text(page)),
            ], spacing=10),
            content=ft.Container(
                ft.Column([
                    ft.Text("Tem certeza que deseja fechar o caixa?",
                            size=13, color=th.text(page)),
                    ft.Text("Um relatório do dia será gerado antes do encerramento.",
                            size=12, color=th.muted(page)),
                ], spacing=6, tight=True, width=340),
                padding=ft.Padding(top=4, bottom=4),
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=_no,
                              style=ft.ButtonStyle(color=th.muted(page))),
                ft.ElevatedButton(
                    "Confirmar fechamento",
                    icon=ft.Icons.CHECK,
                    on_click=_yes,
                    style=ft.ButtonStyle(
                        bgcolor="#FF6B6B",
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=th.RADIUS_BTN),
                        padding=ft.Padding(left=20, top=12, right=20, bottom=12),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            bgcolor=th.surface(page),
            shape=ft.RoundedRectangleBorder(radius=th.RADIUS_CARD),
        )
        ctrl.show_dialog(dialog)

    def run_atendimento():
        if not _operador:
            ctrl.notify("Selecione um operador antes de iniciar.", ok=False)
            show_login()
            return

        color = th.primary(page)

        search_tf    = ctrl.make_text_field("Buscar por nome ou ID", "")
        list_col     = ft.Column(spacing=4, scroll=ft.ScrollMode.ADAPTIVE, height=240)
        clientes_ref = [[]]

        def _row(c):
            cor = _avatar_color(c.id_cliente)
            return ft.Container(
                content=ft.Row([
                    ft.Container(
                        ft.Text(f"#{c.id_cliente}", size=9, color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER),
                        bgcolor=cor, border_radius=4,
                        padding=ft.Padding(left=5, top=2, right=5, bottom=2),
                        width=36, alignment=ft.Alignment(0, 0),
                    ),
                    ft.Text(c.nome, size=12, color=th.text(page), expand=True),
                    ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=11,
                            color=th.muted(page)),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=th.card(page),
                border_radius=8,
                padding=ft.Padding(left=12, top=8, right=12, bottom=8),
                border=ft.Border.all(1, th.border(page)),
                on_click=lambda e, cl=c: _select(cl),
                ink=True,
                ink_color=ft.Colors.with_opacity(0.07, color),
            )

        def _rebuild(query: str) -> None:
            clientes = clientes_ref[0]
            if query:
                lower = query.lower()
                clientes = [
                    c for c in clientes
                    if lower in c.nome.lower() or str(c.id_cliente) == query
                ]
            rows = [_row(c) for c in clientes[:20]]
            nome_query = query.strip()
            nomes_existentes = {c.nome.lower() for c in clientes_ref[0]}
            if (len(nome_query) >= 3
                    and nome_query.lower() not in nomes_existentes):
                rows.append(ft.Container(
                    content=ft.Row([
                        ft.Container(
                            ft.Icon(ft.Icons.PERSON_ADD, size=13, color=color),
                            bgcolor=ft.Colors.with_opacity(0.12, color),
                            border_radius=4, padding=6,
                        ),
                        ft.Text(
                            f"Cadastrar \"{nome_query}\" como novo cliente",
                            size=12, color=color,
                            weight=ft.FontWeight.W_500, expand=True,
                        ),
                        ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=11, color=color),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.Colors.with_opacity(0.06, color),
                    border_radius=8,
                    padding=ft.Padding(left=12, top=8, right=12, bottom=8),
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.3, color)),
                    on_click=lambda e: _create(nome_query),
                    ink=True,
                ))
            list_col.controls = rows or [
                ft.Container(
                    ft.Text("Nenhum cliente encontrado.", size=12,
                            color=th.muted(page)),
                    padding=ft.Padding(left=16, top=16, right=16, bottom=16),
                )
            ]
            page.update()

        def _load() -> None:
            try:
                clientes_ref[0] = SQLAlchemyClienteRepository(_sessao).todos()
            except Exception as ex:
                clientes_ref[0] = []
                ui_call(page, lambda: ctrl.notify(f"Erro ao carregar clientes: {ex}", ok=False))
                return
            ui_call(page, lambda: _rebuild(search_tf.value.strip()))

        search_tf.on_change = lambda e: _rebuild(search_tf.value.strip())

        def _select(cliente) -> None:
            ctrl.close_dialog()
            _start(cliente)

        def _create(nome: str) -> None:
            def _do():
                try:
                    cliente = SQLAlchemyClienteRepository(_sessao).cadastrar(nome)
                    def _after():
                        ctrl.notify(
                            f"Cliente '{cliente.nome}' cadastrado · ID #{cliente.id_cliente}",
                            ok=True,
                        )
                        ctrl.close_dialog()
                        _start(cliente)
                    ui_call(page, _after)
                except Exception as ex:
                    ui_call(page, lambda: ctrl.notify(f"Erro ao cadastrar: {ex}", ok=False))
            threading.Thread(target=_do, daemon=True).start()

        def _start(cliente) -> None:
            def _run():
                try:
                    produto_repo = SQLAlchemyProdutoRepository(_sessao)
                    compra_repo  = SQLAlchemyCompraRepository(_sessao)
                    token        = str(uuid.uuid4())[:8].upper()
                    AtendimentoUseCase(
                        produto_repo, compra_repo,
                        AtendimentoFletAdapter(ctrl, produto_repo),
                    ).atender(
                        cliente.nome, cliente.id_cliente,
                        id_operador=_operador.id_operador if _operador else None,
                        token=token,
                    )
                    time.sleep(2)
                    ui_call(page, show_dashboard)
                except Exception as ex:
                    ui_call(page, lambda: (ctrl.notify(f"Erro: {ex}", ok=False), show_dashboard()))
            threading.Thread(target=_run, daemon=True).start()

        list_col.controls = [
            ft.Container(
                ft.Row([
                    ft.ProgressRing(width=16, height=16, stroke_width=2,
                                    color=color),
                    ft.Text("Carregando clientes...", size=12,
                            color=th.muted(page)),
                ], spacing=8),
                padding=ft.Padding(left=16, top=16, right=16, bottom=16),
            )
        ]

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Container(
                    ft.Icon(ft.Icons.SHOPPING_CART, size=16, color=ft.Colors.WHITE),
                    bgcolor=color,
                    border_radius=8,
                    width=34, height=34, alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text("Novo Atendimento", size=16, weight=ft.FontWeight.BOLD,
                            color=th.text(page)),
                    ft.Text("Selecione ou cadastre o cliente",
                            size=11, color=th.muted(page)),
                ], spacing=1, tight=True),
            ], spacing=10),
            content=ft.Container(
                content=ft.Column(
                    [search_tf, ft.Container(height=4), list_col],
                    spacing=0, tight=True, width=420,
                ),
                padding=ft.Padding(top=4, bottom=4),
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: ctrl.close_dialog(),
                    style=ft.ButtonStyle(color=th.muted(page)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=th.surface(page),
            shape=ft.RoundedRectangleBorder(radius=th.RADIUS_CARD),
        )
        ctrl.show_dialog(dialog)
        threading.Thread(target=_load, daemon=True).start()

    def run_fechar():
        def _run():
            _, produto_repo, compra_repo, _ = _repos()
            CaixaUseCase(compra_repo, produto_repo, CaixaFletAdapter(ctrl)).fechar()
            time.sleep(1)

            try:
                _sessao.commit()
                _sessao.close()
            except Exception:
                pass

            ui_call(page, lambda: ctrl.notify("Caixa fechado com sucesso!", ok=True))
            time.sleep(2)
            ui_call(page, page.window.close)

        threading.Thread(target=_run, daemon=True).start()

    async def on_ready(sessao):
        nonlocal _sessao
        _sessao = sessao
        page.controls.clear()
        page.add(main_layout)
        page.update()
        _set_status(True)
        show_login()
        page.update()  # força reload dos assets SVG após transição

    async def on_error(err):
        page.controls.clear()
        page.add(main_layout)
        page.update()
        ctrl.set_content(
            ctrl.make_card(
                ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=52, color=th.danger(page)),
                    ctrl.make_label("Falha na conexão", size=22, bold=True),
                    ctrl.make_muted(f"Detalhes: {err}"),
                    ctrl.make_primary_btn("Tentar novamente", lambda e: _retry(),
                                         ft.Icons.REFRESH),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                padding=48,
            )
        )

    def _retry():
        SplashPage(ctrl.page, on_ready=on_ready, on_error=on_error).show()

    # ── Content area ──────────────────────────────────────────────
    content_area = ft.Container(
        content=ft.Column([
            ft.Container(
                content=body, 
                expand=True,
                padding=ft.Padding(left=30, right=30, top=10, bottom=30),
            ),
        ], spacing=0, expand=True),
        expand=True,
        bgcolor=th.bg(page),
    )

    # ── Main view ──
    main_layout = ft.Container(
        content=ft.Row([
            sidebar,
            ft.Column([
                navbar,
                content_area,
                footer,
            ], spacing=0, expand=True),
        ], spacing=0, expand=True),
        expand=True,
    )

    # ── Assemble ──────────────────────────────────────────────────
    page.add(main_layout)

    _start_clock()
    SplashPage(ctrl.page, on_ready=on_ready, on_error=on_error).show()

import flet as ft

from app.domain.models import Operador
from app.flet.controller import PageController
from app.flet import theme as th
from app.flet.operators import buscar_por_id


class LoginPage:
    def __init__(self, ctrl: PageController, operadores: list[Operador], on_login):
        self._ctrl = ctrl
        self._operadores = operadores
        self._on_login = on_login

    def show(self) -> None:
        page = self._ctrl.page

        self._ctrl.set_content(
            ft.Column([
                self._build_header(page),
                ft.Container(height=24),
                ft.Text(
                    "Selecione o operador para iniciar",
                    size=14,
                    color=th.muted(page),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=16),
                ft.Row(
                    [self._build_operator_card(op) for op in self._operadores],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=16,
                    wrap=True,
                ),
                ft.Container(height=20),
                ft.Divider(color=th.border(page)),
                ft.Container(height=8),
                self._build_id_input(page),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
        )

    def _build_header(self, page: ft.Page) -> ft.Container:
        dark = th.is_dark(page)
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Image(src="/logo.svg", width=140, height=76, fit="contain"),
                    margin=ft.Margin(bottom=10),
                ),
                ft.Text(
                    "CAIXA MERCADO",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                    style=ft.TextStyle(letter_spacing=2),
                ),
                ft.Text(
                    "AUTENTICAÇÃO DO OPERADOR",
                    size=12,
                    color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
                    text_align=ft.TextAlign.CENTER,
                    weight=ft.FontWeight.W_600,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            bgcolor=ft.Colors.TRANSPARENT,
            padding=ft.Padding(left=48, top=20, right=48, bottom=20),
            width=520,
        )

    def _build_operator_card(self, op: Operador) -> ft.Container:
        page = self._ctrl.page
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    ft.Text(op.iniciais, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=op.cor,
                    border_radius=40,
                    width=70,
                    height=70,
                    alignment=ft.Alignment(0, 0),
                    shadow=[ft.BoxShadow(
                        blur_radius=15,
                        color=ft.Colors.with_opacity(0.4, op.cor),
                        offset=ft.Offset(0, 5),
                    )],
                ),
                ft.Container(height=14),
                ft.Text(
                    op.nome.split()[0],
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=th.text(page),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    op.cargo.upper(),
                    size=9,
                    color=th.muted(page),
                    weight=ft.FontWeight.W_600,
                    text_align=ft.TextAlign.CENTER,
                    style=ft.TextStyle(letter_spacing=1),
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            bgcolor=th.card(page),
            border_radius=th.RADIUS_CARD,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.1, th.text(page))),
            shadow=th.card_shadows(th.is_dark(page)),
            padding=ft.Padding(left=24, top=24, right=24, bottom=24),
            width=130,
            alignment=ft.Alignment(0, 0),
            ink=True,
            ink_color=ft.Colors.with_opacity(0.1, op.cor),
            on_click=lambda e, o=op: self._on_login(o),
        )

    def _build_id_input(self, page: ft.Page) -> ft.Container:
        tf = self._ctrl.make_text_field("Ou digite o ID do operador", "Ex: 1", ft.KeyboardType.NUMBER)
        tf.width = 240

        operadores = self._operadores

        def _submit(e):
            try:
                val = int(tf.value.strip())
            except ValueError:
                self._ctrl.notify("ID inválido.", ok=False)
                return
            op = buscar_por_id(operadores, val)
            if op is None:
                self._ctrl.notify(f"Operador #{val} não encontrado.", ok=False)
                return
            self._on_login(op)

        tf.on_submit = _submit
        return ft.Row([
            tf,
            self._ctrl.make_primary_btn("Entrar", _submit, ft.Icons.LOGIN),
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)

import flet as ft

from app.flet.controller import PageController
from app.flet import theme as th
from app.shared.ui_helpers import avatar_color as _palette_color, initials as _initials


_FILTRO_TODOS    = "Todos"
_FILTRO_CRITICO  = "Crítico"
_FILTRO_BAIXO    = "Baixo"
_FILTRO_NORMAL   = "Normal"
_FILTROS         = [_FILTRO_TODOS, _FILTRO_CRITICO, _FILTRO_BAIXO, _FILTRO_NORMAL]


def _urgencia(produto) -> int:
    """Lower value = higher urgency for sorting."""
    if produto.quantidade == 0:
        return 0
    if produto.quantidade <= 2:
        return 1
    if produto.quantidade <= 5:
        return 2
    return 3


def _classificar(produto) -> str:
    if produto.quantidade == 0:
        return "Esgotado"
    if produto.quantidade <= 2:
        return _FILTRO_CRITICO
    if produto.quantidade <= 5:
        return _FILTRO_BAIXO
    return _FILTRO_NORMAL


class EstoquePage:

    def __init__(self, ctrl: PageController, produto_repo):
        self._ctrl = ctrl
        self._repo = produto_repo
        self._filtro_ativo = _FILTRO_TODOS

    def show(self) -> None:
        produtos = self._repo.todos()
        async def _render_async():
            self._render(produtos)
        self._ctrl.page.run_task(_render_async)

    def _render(self, produtos: list) -> None:
        page = self._ctrl.page

        total_produtos = len(produtos)
        em_estoque     = sum(1 for p in produtos if p.quantidade > 0)
        sem_estoque    = total_produtos - em_estoque
        valor_total    = sum(float(p.preco) * p.quantidade for p in produtos)

        lista_ref  = ft.Ref[ft.Column]()
        filtro_ref = ft.Ref[ft.Row]()

        def _aplicar_filtro(filtro: str, e=None) -> None:
            self._filtro_ativo = filtro
            filtro_ref.current.controls = _build_filter_row()
            lista_ref.current.controls  = _build_rows(filtro)
            page.update()

        def _build_filter_row() -> list:
            btns = []
            for f in _FILTROS:
                ativo = f == self._filtro_ativo
                cor   = th.primary(page)
                btns.append(
                    ft.Container(
                        content=ft.Text(
                            f, size=11,
                            weight=ft.FontWeight.BOLD if ativo else ft.FontWeight.NORMAL,
                            color=ft.Colors.WHITE if ativo else th.text(page),
                        ),
                        bgcolor=cor if ativo else ft.Colors.with_opacity(0.06, cor),
                        border=ft.border.all(1, cor if ativo
                                             else ft.Colors.with_opacity(0.3, cor)),
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=14, vertical=6),
                        ink=True,
                        ink_color=ft.Colors.with_opacity(0.08, cor),
                        on_click=lambda e, fil=f: _aplicar_filtro(fil),
                    )
                )
            return btns

        def _build_rows(filtro: str) -> list:
            ordenados = sorted(produtos, key=_urgencia)
            if filtro == _FILTRO_CRITICO:
                selecionados = [p for p in ordenados if p.quantidade <= 2]
            elif filtro == _FILTRO_BAIXO:
                selecionados = [p for p in ordenados
                                if 3 <= p.quantidade <= 5]
            elif filtro == _FILTRO_NORMAL:
                selecionados = [p for p in ordenados if p.quantidade > 5]
            else:
                selecionados = ordenados

            if not selecionados:
                return [ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF, size=34, color=th.muted(page)),
                        ft.Text("Nenhum produto nesta categoria.", size=13,
                                color=th.muted(page)),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.padding.symmetric(vertical=24),
                )]

            rows = []
            for p in selecionados:
                color      = _palette_color(p.id_produto)
                classe     = _classificar(p)
                esgotado   = p.quantidade == 0
                critico    = p.quantidade <= 2 and not esgotado
                baixo      = 3 <= p.quantidade <= 5

                if esgotado:
                    status_label = "Esgotado"
                    status_color = th.danger(page)
                elif critico:
                    status_label = "Crítico"
                    status_color = th.danger(page)
                elif baixo:
                    status_label = "Baixo"
                    status_color = th.DARK_WARNING
                else:
                    status_label = "Normal"
                    status_color = th.success(page)

                avatar_bg = color if not esgotado else th.muted(page)

                alert_badge = None
                if critico:
                    alert_badge = ft.Container(
                        content=ft.Text("CRÍTICO", size=8,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE),
                        bgcolor=th.danger(page),
                        border_radius=4,
                        padding=ft.padding.symmetric(horizontal=5, vertical=2),
                        animate_opacity=ft.Animation(800, ft.AnimationCurve.EASE_IN_OUT),
                        opacity=1.0,
                    )

                qty_container = ft.Container(
                    ft.Text(str(p.quantidade), size=12,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER),
                    bgcolor=status_color,
                    border_radius=6,
                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                    width=52,
                    alignment=ft.Alignment(0, 0),
                )

                name_col = ft.Row([
                    ft.Text(p.nome, size=13, color=th.text(page),
                            expand=True, weight=ft.FontWeight.W_500,
                            overflow=ft.TextOverflow.ELLIPSIS),
                    alert_badge if alert_badge else ft.Container(),
                ], spacing=6, expand=True,
                   vertical_alignment=ft.CrossAxisAlignment.CENTER)

                rows.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                ft.Text(_initials(p.nome), size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE,
                                        text_align=ft.TextAlign.CENTER),
                                bgcolor=avatar_bg,
                                border_radius=50,
                                width=38, height=38,
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Container(
                                ft.Text(f"#{p.id_produto}", size=10,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.BOLD),
                                bgcolor=avatar_bg,
                                border_radius=4,
                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                width=38,
                            ),
                            name_col,
                            ft.Text(f"R$ {p.preco:.2f}", size=13,
                                    color=th.accent(page), width=80,
                                    weight=ft.FontWeight.W_600),
                            qty_container,
                            ft.Container(
                                ft.Text(status_label, size=10,
                                        color=status_color,
                                        weight=ft.FontWeight.W_600),
                                border=ft.border.all(1, status_color),
                                border_radius=4,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                width=64,
                            ),
                        ], spacing=12,
                           vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=th.card(page),
                        border_radius=10,
                        border=ft.border.all(
                            1,
                            ft.Colors.with_opacity(0.35, th.danger(page)) if critico or esgotado
                            else ft.Colors.with_opacity(0.25, th.DARK_WARNING) if baixo
                            else ft.Colors.with_opacity(0.15, color),
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        opacity=0.55 if esgotado else 1.0,
                        margin=ft.margin.only(bottom=6),
                    )
                )
            return rows

        header_row = ft.Container(
            ft.Row([
                ft.Container(
                    ft.Icon(ft.Icons.FORMAT_LIST_BULLETED, size=14,
                            color=th.primary(page)),
                    bgcolor=ft.Colors.with_opacity(0.10, th.primary(page)),
                    border_radius=6, padding=6,
                ),
                ft.Text("Produtos cadastrados", size=13,
                        weight=ft.FontWeight.BOLD, color=th.text(page)),
                ft.Container(expand=True),
                ft.Row(ref=filtro_ref,
                       controls=_build_filter_row(),
                       spacing=6),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        )

        col_header = ft.Container(
            ft.Row([
                ft.Container(width=38),
                ft.Container(width=38),
                ft.Text("Produto", size=11, color=th.muted(page), expand=True),
                ft.Text("Preço", size=11, color=th.muted(page), width=80),
                ft.Text("Qtd", size=11, color=th.muted(page), width=52,
                        text_align=ft.TextAlign.CENTER),
                ft.Text("Status", size=11, color=th.muted(page), width=64),
            ], spacing=12),
            padding=ft.padding.symmetric(horizontal=16, vertical=6),
        )

        lista = ft.Column(ref=lista_ref, controls=_build_rows(_FILTRO_TODOS), spacing=0)

        tabela = self._ctrl.make_card(
            ft.Column([
                header_row,
                ft.Divider(color=th.border(page)),
                col_header,
                ft.Divider(color=th.border(page), height=1),
                lista,
            ], spacing=10),
            padding=18,
        ) if produtos else self._ctrl.make_card(
            ft.Column([
                ft.Icon(ft.Icons.INVENTORY_2, size=44, color=th.muted(page)),
                ft.Text("Nenhum produto cadastrado.", size=14, color=th.muted(page)),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
            padding=48,
        )

        self._ctrl.set_content(
            ft.Column([
                self._build_header(page),
                ft.Container(height=4),
                self._build_summary(page, total_produtos, em_estoque,
                                    sem_estoque, valor_total),
                ft.Container(height=16),
                tabela,
            ], spacing=0),
        )

    def _build_header(self, page: ft.Page) -> ft.Row:
        return ft.Row([
            ft.Container(
                ft.Icon(ft.Icons.INVENTORY_2, size=16,
                        color=th.primary(page)),
                bgcolor=ft.Colors.with_opacity(0.12, th.primary(page)),
                border_radius=8, padding=8,
            ),
            ft.Column([
                ft.Text("Estoque", size=20, weight=ft.FontWeight.BOLD,
                        color=th.text(page)),
                ft.Text("Visão geral dos produtos cadastrados",
                        size=12, color=th.muted(page)),
            ], spacing=2, tight=True),
        ], spacing=12)

    def _build_summary(self, page, total, em, sem, valor) -> ft.Row:
        def card(icon, label, value, color):
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
                    ft.Text(str(value), size=20, weight=ft.FontWeight.BOLD,
                            color=th.text(page)),
                    ft.Text(label, size=11, color=th.muted(page)),
                ], spacing=2, tight=True),
                bgcolor=th.card(page),
                border_radius=th.RADIUS_CARD,
                shadow=th.card_shadows(th.is_dark(page)),
                padding=ft.padding.all(16),
                expand=True,
            )

        return ft.Row([
            card(ft.Icons.INVENTORY,     "Total de produtos", total,
                 th.primary(page)),
            card(ft.Icons.CHECK_CIRCLE,  "Em estoque", em,
                 th.success(page)),
            card(ft.Icons.CANCEL,        "Sem estoque", sem,
                 th.danger(page)),
            card(ft.Icons.ATTACH_MONEY,  "Valor total (R$)",
                 f"{valor:,.2f}", "#FFB700"),
        ], spacing=14, vertical_alignment=ft.CrossAxisAlignment.STRETCH)

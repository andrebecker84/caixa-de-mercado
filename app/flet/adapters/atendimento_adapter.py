from datetime import datetime
from decimal import Decimal

import flet as ft

from app.core.ports import AtendimentoPort
from app.flet.bridge import InputBridge
from app.flet.controller import PageController, ui_call
from app.flet import theme as th


from app.shared.ui_helpers import avatar_color as _avatar_color, initials as _initials


class AtendimentoFletAdapter(AtendimentoPort):

    def __init__(self, ctrl: PageController, produto_repo=None):
        self._ctrl = ctrl
        self._produto_repo  = produto_repo
        self._bridge        = InputBridge()
        self._produtos:     list = []
        self._initial_qty:  dict[int, int] = {}
        self._carrinho:     list = []
        self._cart_ref      = ft.Column(spacing=4)
        self._products_grid = ft.GridView(
            max_extent=160,
            spacing=8,
            run_spacing=8,
            child_aspect_ratio=0.88,
        )
        self._code_section  = ft.Column(spacing=8)
        self._cancelados:   list = []
        self._pending_qty:  int  = 0
        self._modal_mode:   bool = False

    # ── Port implementation ────────────────────────────────────────

    def exibir_inicio(self, cliente_nome: str) -> None:
        page = self._ctrl.page
        self._ctrl.set_content(
            self._ctrl.make_card(
                ft.Row([
                    ft.Container(
                        ft.Icon(ft.Icons.SHOPPING_CART, size=24,
                                color=th.primary(page)),
                        bgcolor=ft.Colors.with_opacity(0.12, th.primary(page)),
                        border_radius=10, padding=10,
                    ),
                    ft.Column([
                        self._ctrl.make_label("Atendimento em andamento",
                                              size=18, bold=True),
                        self._ctrl.make_muted(f"Cliente: {cliente_nome}"),
                    ], spacing=2, tight=True),
                ], spacing=14),
                padding=18,
            )
        )

    def exibir_produtos(self, produtos: list) -> None:
        self._produtos    = produtos
        self._initial_qty = {p.id_produto: p.quantidade for p in produtos}
        ui_call(self._ctrl.page, self._mostrar_layout_compra)

    def pedir_id_produto(self) -> int:
        self._modal_mode  = False
        self._pending_qty = 0
        ui_call(self._ctrl.page, self._mostrar_layout_compra)
        return self._bridge.wait()

    def _mostrar_layout_compra(self) -> None:
        self._rebuild_id_input()
        self._ctrl.set_content(self._build_shopping_layout())

    def pedir_quantidade(self, nome: str) -> int:
        return self._pending_qty if self._modal_mode else 1

    def confirmar_adicao(self, nome: str, quantidade: int) -> bool:
        return True

    def exibir_item_adicionado(self, nome: str, carrinho: list) -> None:
        self._carrinho = carrinho
        page = self._ctrl.page
        def _update():
            self._ctrl.notify(f"'{nome}' adicionado ao carrinho.", ok=True)
            self._populate_cart()
            self._populate_products()
            page.update()
        ui_call(page, _update)

    def exibir_item_nao_adicionado(self, nome: str) -> None:
        ui_call(self._ctrl.page,
            lambda: self._ctrl.notify(f"'{nome}' não adicionado.", ok=False)
        )

    def exibir_carrinho(self, cliente_nome: str, carrinho: list,
                        cancelados: list, total: Decimal) -> None:
        self._carrinho   = carrinho
        self._cancelados = cancelados
        page = self._ctrl.page
        data = datetime.now().strftime("%d/%m/%Y %H:%M")

        def _do_mais(e):
            self._ctrl.close_dialog()
            self._bridge.resolve(2)

        def _do_confirm(e):
            self._ctrl.close_dialog()
            self._bridge.resolve(1)

        def _do_cancel(e):
            self._ctrl.close_dialog()
            self._bridge.resolve(0)

        rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(i + 1), size=12, color=th.muted(page))),
                ft.DataCell(ft.Text(item.nome, size=12, color=th.text(page),
                                    weight=ft.FontWeight.W_500)),
                ft.DataCell(ft.Text(str(item.quantidade), size=12, color=th.text(page))),
                ft.DataCell(ft.Text(f"R$ {item.preco_unitario:.2f}", size=12,
                                    color=th.muted(page))),
                ft.DataCell(ft.Text(f"R$ {item.subtotal:.2f}", size=12,
                                    color=th.accent(page),
                                    weight=ft.FontWeight.W_600)),
            ])
            for i, item in enumerate(carrinho)
        ]

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("#",        size=11, color=th.muted(page))),
                ft.DataColumn(ft.Text("Produto",  size=11, color=th.muted(page))),
                ft.DataColumn(ft.Text("Qtd",      size=11, color=th.muted(page))),
                ft.DataColumn(ft.Text("Preço",    size=11, color=th.muted(page))),
                ft.DataColumn(ft.Text("Subtotal", size=11, color=th.muted(page))),
            ],
            rows=rows,
            column_spacing=14,
            heading_row_height=34,
            data_row_min_height=32,
        )

        cancelled_section = []
        if cancelados:
            cancelled_section = [
                ft.Divider(color=th.border(page)),
                ft.Text(
                    f"Cancelados: {', '.join(i.nome for i in cancelados)}",
                    size=11, color=th.danger(page),
                ),
            ]

        content = ft.Column([
            ft.Row([
                ft.Text(f"Cliente: {cliente_nome}", size=12, color=th.muted(page)),
                ft.Text(data, size=12, color=th.muted(page)),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(color=th.border(page)),
            table,
            ft.Divider(color=th.border(page)),
            ft.Row([
                ft.Text("Total da compra", size=13, weight=ft.FontWeight.BOLD,
                        color=th.text(page)),
                ft.Text(f"R$ {total:.2f}", size=17, weight=ft.FontWeight.BOLD,
                        color=th.success(page)),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            *cancelled_section,
        ], spacing=10, tight=True, width=520)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Container(
                    ft.Icon(ft.Icons.RECEIPT_LONG, size=16, color=ft.Colors.WHITE),
                    bgcolor=th.primary(page),
                    border_radius=ft.border_radius.all(8),
                    width=34, height=34, alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text("Nota Fiscal", size=16, weight=ft.FontWeight.BOLD,
                            color=th.text(page)),
                    ft.Text("Revise os itens antes de confirmar",
                            size=11, color=th.muted(page)),
                ], spacing=1, tight=True),
            ], spacing=10),
            content=ft.Container(
                content=content,
                padding=ft.padding.only(top=4, bottom=4),
            ),
            actions=[
                ft.TextButton(
                    "Cancelar", on_click=_do_cancel,
                    style=ft.ButtonStyle(color=th.danger(page)),
                ),
                ft.OutlinedButton(
                    "Adicionar mais",
                    icon=ft.Icons.ADD_SHOPPING_CART,
                    on_click=_do_mais,
                    style=ft.ButtonStyle(
                        color=th.primary(page),
                        side=ft.BorderSide(color=th.primary(page), width=1),
                        shape=ft.RoundedRectangleBorder(radius=th.RADIUS_BTN),
                        padding=ft.padding.symmetric(horizontal=14, vertical=10),
                    ),
                ),
                self._ctrl.make_primary_btn(
                    "Confirmar compra", _do_confirm, ft.Icons.CHECK
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            bgcolor=th.surface(page),
            shape=ft.RoundedRectangleBorder(radius=th.RADIUS_CARD),
        )
        ui_call(self._ctrl.page, lambda: self._ctrl.show_dialog(dialog))

    def confirmar_compra(self) -> int:
        return self._bridge.wait()

    def exibir_compra_cancelada(self) -> None:
        page = self._ctrl.page
        ui_call(page,
            lambda: self._ctrl.set_content(
                self._ctrl.make_card(
                    ft.Column([
                        ft.Icon(ft.Icons.CANCEL, size=52, color=th.danger(page)),
                        self._ctrl.make_label("Compra cancelada", size=22, bold=True),
                        self._ctrl.make_muted("Estoque liberado automaticamente."),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                    padding=40,
                )
            )
        )

    def exibir_compra_registrada(self, id_compra: int) -> None:
        page = self._ctrl.page
        ui_call(page,
            lambda: self._ctrl.set_content(
                self._ctrl.make_card(
                    ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=52, color=th.success(page)),
                        self._ctrl.make_label(
                            "Compra registrada!", size=22, bold=True,
                            color=th.success(page),
                        ),
                        self._ctrl.make_muted(f"Nº da venda: #{id_compra}"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                    padding=40,
                )
            )
        )

    def exibir_erro(self, mensagem: str) -> None:
        ui_call(self._ctrl.page,
            lambda: self._ctrl.notify(mensagem, ok=False)
        )

    # ── Shopping layout ───────────────────────────────────────────

    def _build_shopping_layout(self) -> ft.Row:
        self._populate_cart()
        self._populate_products()
        return ft.Row([
            ft.Column([self._build_products_card()], expand=2, spacing=0),
            ft.Column([self._build_cart_card()],     expand=3, spacing=0),
        ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.START)

    # ── Products panel ────────────────────────────────────────────

    def _build_products_card(self) -> ft.Container:
        page = self._ctrl.page
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        ft.Icon(ft.Icons.INVENTORY_2, size=14,
                                color=th.primary(page)),
                        bgcolor=ft.Colors.with_opacity(0.12, th.primary(page)),
                        border_radius=8, padding=7,
                    ),
                    ft.Column([
                        self._ctrl.make_label("Produtos", bold=True),
                        self._ctrl.make_muted("Arraste ou clique em +", size=10),
                    ], spacing=1, tight=True, expand=True),
                ], spacing=10),
                ft.Divider(color=th.border(page)),
                ft.Container(
                    content=self._products_grid,
                    height=360,
                ),
                ft.Divider(color=th.border(page)),
                self._code_section,
            ], spacing=10),
            bgcolor=th.card(page),
            border_radius=ft.border_radius.all(th.RADIUS_CARD),
            shadow=th.card_shadows(th.is_dark(page)),
            padding=18,
        )

    def _build_product_grid_item(self, produto) -> ft.Control:
        page     = self._ctrl.page
        disp     = self._qty_disponivel(produto)
        esgotado = disp <= 0
        color    = _avatar_color(produto.id_produto)
        ini      = _initials(produto.nome)
        primary  = th.primary(page)

        if esgotado:
            stock_color = th.danger(page)
        elif disp <= 3:
            stock_color = th.DARK_WARNING
        else:
            stock_color = th.success(page)

        def _open(e, p=produto):
            d = self._qty_disponivel(p)
            if d <= 0:
                self._ctrl.notify("Produto sem estoque.", ok=False)
                return
            self._open_product_modal(p, d)

        avatar = ft.Container(
            content=ft.Text(
                ini, size=13, weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER,
            ),
            bgcolor=color if not esgotado else th.muted(page),
            border_radius=ft.border_radius.all(50),
            width=40, height=40,
            alignment=ft.Alignment(0, 0),
            shadow=[ft.BoxShadow(
                blur_radius=6,
                color=ft.Colors.with_opacity(0.25, color),
                offset=ft.Offset(0, 2),
            )] if not esgotado else None,
        )

        id_badge = ft.Container(
            ft.Text(f"#{produto.id_produto}", size=8,
                    color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER),
            bgcolor=color if not esgotado else th.muted(page),
            border_radius=3,
            padding=ft.padding.symmetric(horizontal=4, vertical=1),
        )

        stock_badge = ft.Container(
            ft.Text(
                f"{disp}" if not esgotado else "—",
                size=9, color=ft.Colors.WHITE,
                weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,
            ),
            bgcolor=stock_color,
            border_radius=4,
            padding=ft.padding.symmetric(horizontal=5, vertical=2),
            tooltip=f"{disp} unidades disponíveis" if not esgotado else "Esgotado",
        )

        add_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD_ROUNDED, size=16, color=ft.Colors.WHITE if not esgotado else th.muted(page)),
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=primary if not esgotado else ft.Colors.with_opacity(0.1, th.muted(page)),
            border_radius=12,
            width=32, height=32,
            on_click=_open if not esgotado else None,
            ink=not esgotado,
            ink_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
        )

        card = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text(ini, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=color if not esgotado else th.muted(page),
                    width=48, height=48,
                    border_radius=24,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(height=4),
                ft.Text(
                    produto.nome,
                    size=12, weight=ft.FontWeight.BOLD,
                    color=th.text(page),
                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    f"R$ {produto.preco:.2f}",
                    size=13, weight=ft.FontWeight.BOLD,
                    color=th.primary(page),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=4),
                ft.Row([
                    ft.Text(f"{disp} disp.", size=9, color=th.muted(page)),
                    add_btn,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=2, tight=True),
            bgcolor=th.card(page),
            border_radius=th.RADIUS_CARD,
            padding=ft.padding.all(12),
            opacity=0.5 if esgotado else 1.0,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, th.text(page))),
        )

        if esgotado:
            return card

        return ft.Draggable(
            group="cart",
            data=str(produto.id_produto),
            content=card,
            content_when_dragging=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.DRAG_INDICATOR,
                            color=th.muted(page), size=18),
                    ft.Text(
                        produto.nome[:12],
                        size=9, color=th.muted(page),
                        text_align=ft.TextAlign.CENTER,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
                bgcolor=ft.Colors.with_opacity(0.3, th.card(page)),
                border_radius=ft.border_radius.all(th.RADIUS_CARD),
                border=ft.border.all(1, th.border(page)),
                padding=ft.padding.all(10),
            ),
            content_feedback=ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.SHOPPING_CART, size=12,
                            color=ft.Colors.WHITE),
                    ft.Text(
                        produto.nome[:16], size=11, color=ft.Colors.WHITE,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ], spacing=6, tight=True),
                bgcolor=primary,
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                shadow=[ft.BoxShadow(
                    blur_radius=14,
                    color=ft.Colors.with_opacity(0.35, ft.Colors.BLACK),
                    offset=ft.Offset(0, 4),
                )],
            ),
        )

    # ── Cart panel ────────────────────────────────────────────────

    def _build_cart_card(self) -> ft.Container:
        page = self._ctrl.page

        cart_body = ft.Column([
            ft.Row([
                ft.Container(
                    ft.Icon(ft.Icons.SHOPPING_CART, size=14,
                            color=th.primary(page)),
                    bgcolor=ft.Colors.with_opacity(0.12, th.primary(page)),
                    border_radius=8, padding=7,
                ),
                ft.Column([
                    self._ctrl.make_label("Carrinho", bold=True),
                    self._ctrl.make_muted("Solte produtos aqui · clique [×] para remover",
                                          size=10),
                ], spacing=1, tight=True, expand=True),
            ], spacing=10),
            ft.Divider(color=th.border(page)),
            self._cart_ref,
        ], spacing=10)

        finalizar_btn = ft.ElevatedButton(
            "Finalizar Compra",
            icon=ft.Icons.RECEIPT_LONG,
            on_click=lambda e: self._bridge.resolve(0),
            style=ft.ButtonStyle(
                bgcolor=th.primary(page),
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=th.RADIUS_BTN),
                padding=ft.padding.symmetric(horizontal=24, vertical=14),
            ),
        )

        return ft.Container(
            content=ft.Column([
                ft.DragTarget(
                    group="cart",
                    content=cart_body,
                    on_accept=self._on_drag_accept,
                    on_will_accept=lambda e: True,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("SUBTOTAL", size=12, color=th.muted(page), weight=ft.FontWeight.BOLD),
                            ft.Text(f"R$ {sum(i.subtotal for i in self._carrinho):,.2f}", size=14, color=th.text(page), weight=ft.FontWeight.BOLD),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(height=10),
                        finalizar_btn,
                    ]),
                    padding=ft.padding.all(20),
                    bgcolor=ft.Colors.with_opacity(0.05, th.text(page)),
                    border_radius=th.RADIUS_CARD,
                ),
            ], spacing=10, expand=True),
            bgcolor=th.card(page),
            border_radius=th.RADIUS_CARD,
            padding=20,
            expand=True,
        )

    # ── Code input ────────────────────────────────────────────────

    def _rebuild_id_input(self) -> None:
        page         = self._ctrl.page
        tf           = self._ctrl.make_text_field(
            "ID do produto (0 = finalizar)", "ex: 3", ft.KeyboardType.NUMBER
        )
        tf.dense     = True
        name_preview = ft.Text("", size=12, color=th.accent(page))

        def _on_change(e):
            raw = tf.value.strip()
            if not raw:
                name_preview.value = ""
                page.update()
                return
            try:
                val     = int(raw)
                produto = next(
                    (p for p in self._produtos if p.id_produto == val), None
                )
                if produto:
                    disp = self._qty_disponivel(produto)
                    name_preview.value = (
                        f"{produto.nome}  ·  R$ {produto.preco:.2f}"
                        f"  ·  {disp} disponível{'is' if disp != 1 else ''}"
                    )
                    name_preview.color = th.accent(page)
                else:
                    name_preview.value = "Produto não encontrado"
                    name_preview.color = th.danger(page)
            except ValueError:
                name_preview.value = ""
            page.update()

        def _submit(e):
            raw = tf.value.strip()
            try:
                val = int(raw)
            except ValueError:
                self._ctrl.notify("Digite um número inteiro.", ok=False)
                return
            if val == 0:
                self._bridge.resolve(0)
                return
            if val < 0:
                self._ctrl.notify("ID inválido.", ok=False)
                return
            produto = next(
                (p for p in self._produtos if p.id_produto == val), None
            )
            if produto is None:
                self._ctrl.notify(f"Produto #{val} não encontrado.", ok=False)
                tf.value = ""
                name_preview.value = ""
                page.update()
                return
            self._open_product_modal(produto, self._qty_disponivel(produto))

        tf.on_change = _on_change
        tf.on_submit = _submit

        self._code_section.controls = [
            self._ctrl.make_label("Busca por código", bold=True, size=12),
            tf,
            name_preview,
            self._ctrl.make_primary_btn(
                "Adicionar", _submit, ft.Icons.ADD_SHOPPING_CART
            ),
        ]

    # ── Product modal ─────────────────────────────────────────────

    def _open_product_modal(self, produto, disponivel: int) -> None:
        if disponivel <= 0:
            self._ctrl.notify("Produto sem estoque disponível.", ok=False)
            return

        page    = self._ctrl.page
        qty_ref = [1]

        qty_display = ft.Text(
            "1", size=30, weight=ft.FontWeight.BOLD,
            color=th.primary(page), text_align=ft.TextAlign.CENTER, width=70,
        )
        unit_lbl = ft.Text(
            f"de {disponivel} disponível{'is' if disponivel > 1 else ''}",
            size=11, color=th.muted(page),
        )
        subtotal_lbl = ft.Text(
            f"Subtotal: R$ {produto.preco:.2f}",
            size=13, color=th.success(page), weight=ft.FontWeight.W_600,
        )
        slider = ft.Slider(
            min=1, max=float(disponivel), value=1.0,
            divisions=max(1, disponivel - 1),
            active_color=th.primary(page),
            inactive_color=ft.Colors.with_opacity(0.15, th.primary(page)),
        )

        def _update(val: int) -> None:
            val                = max(1, min(val, disponivel))
            qty_ref[0]         = val
            qty_display.value  = str(val)
            slider.value       = float(val)
            subtotal_lbl.value = f"Subtotal: R$ {produto.preco * val:.2f}"
            page.update()

        def _slider_change(e):
            if e.data:
                _update(int(float(e.data)))

        slider.on_change = _slider_change

        def _dec(e=None): _update(qty_ref[0] - 1)
        def _inc(e=None): _update(qty_ref[0] + 1)

        def _do_add(e):
            self._ctrl.close_dialog()
            self._modal_mode  = True
            self._pending_qty = qty_ref[0]
            self._bridge.resolve(produto.id_produto)

        def _do_cancel(e):
            self._ctrl.close_dialog()

        stock_badge_color = (
            th.danger(page) if disponivel <= 3 else th.success(page)
        )
        color = _avatar_color(produto.id_produto)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Container(
                    ft.Text(_initials(produto.nome), size=14,
                            weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER),
                    bgcolor=color, border_radius=ft.border_radius.all(50),
                    width=36, height=36, alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(produto.nome, size=15, weight=ft.FontWeight.BOLD,
                            color=th.text(page)),
                    ft.Text(f"Código #{produto.id_produto}", size=10,
                            color=th.muted(page)),
                ], spacing=1, tight=True),
            ], spacing=10),
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text(f"R$ {produto.preco:.2f}", size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=th.accent(page)),
                            ft.Text("por unidade", size=10,
                                    color=th.muted(page)),
                        ], spacing=2, tight=True),
                        ft.Container(
                            content=ft.Column([
                                ft.Text(str(disponivel), size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE,
                                        text_align=ft.TextAlign.CENTER),
                                ft.Text("em estoque", size=9,
                                        color=ft.Colors.with_opacity(
                                            0.8, ft.Colors.WHITE),
                                        text_align=ft.TextAlign.CENTER),
                            ], spacing=1,
                               horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            bgcolor=stock_badge_color,
                            border_radius=10,
                            padding=ft.padding.symmetric(horizontal=14,
                                                         vertical=10),
                            shadow=[ft.BoxShadow(
                                blur_radius=8,
                                color=ft.Colors.with_opacity(
                                    0.25, stock_badge_color),
                                offset=ft.Offset(0, 3),
                            )],
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(color=th.border(page)),
                    ft.Text("Quantidade", size=12, color=th.muted(page),
                            weight=ft.FontWeight.W_500),
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                            icon_color=th.primary(page), icon_size=24,
                            on_click=_dec,
                            style=ft.ButtonStyle(
                                shape=ft.CircleBorder(), padding=4
                            ),
                        ),
                        ft.Column([qty_display, unit_lbl],
                                  horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                  spacing=2, tight=True),
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                            icon_color=th.primary(page), icon_size=24,
                            on_click=_inc,
                            style=ft.ButtonStyle(
                                shape=ft.CircleBorder(), padding=4
                            ),
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
                    slider,
                    ft.Container(
                        content=subtotal_lbl,
                        bgcolor=ft.Colors.with_opacity(0.06, th.success(page)),
                        border_radius=8,
                        padding=ft.padding.symmetric(horizontal=14, vertical=8),
                    ),
                ], spacing=14, tight=True, width=340),
                padding=ft.padding.only(top=4, bottom=4),
            ),
            actions=[
                ft.TextButton(
                    "Cancelar", on_click=_do_cancel,
                    style=ft.ButtonStyle(color=th.muted(page)),
                ),
                self._ctrl.make_primary_btn(
                    "Adicionar ao Carrinho", _do_add, ft.Icons.ADD_SHOPPING_CART
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            bgcolor=th.surface(page),
            shape=ft.RoundedRectangleBorder(radius=th.RADIUS_CARD),
        )
        self._ctrl.show_dialog(dialog)

    def _on_drag_accept(self, e) -> None:
        try:
            src        = self._ctrl.page.get_control(e.src_id)
            id_produto = int(src.data)
        except (ValueError, TypeError, AttributeError):
            return
        produto = next(
            (p for p in self._produtos if p.id_produto == id_produto), None
        )
        if produto is None:
            return
        disp = self._qty_disponivel(produto)
        if disp <= 0:
            self._ctrl.notify("Produto sem estoque.", ok=False)
            return
        self._open_product_modal(produto, disp)

    # ── Cart item removal ─────────────────────────────────────────

    def _remove_item(self, item) -> None:
        self._carrinho = [i for i in self._carrinho if i is not item]
        if self._produto_repo:
            try:
                self._produto_repo.liberar(item.id_produto, item.quantidade)
            except RuntimeError:
                pass
        self._populate_cart()
        self._populate_products()
        self._ctrl.page.update()

    # ── Helpers ───────────────────────────────────────────────────

    def _qty_disponivel(self, produto) -> int:
        initial   = self._initial_qty.get(produto.id_produto, 0)
        reservado = sum(
            item.quantidade for item in self._carrinho
            if item.id_produto == produto.id_produto
        )
        return initial - reservado

    def _populate_products(self) -> None:
        self._products_grid.controls = [
            self._build_product_grid_item(p) for p in self._produtos
        ]

    def _populate_cart(self) -> None:
        page = self._ctrl.page
        if not self._carrinho:
            self._cart_ref.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, size=44,
                                color=th.muted(page)),
                        ft.Text("Carrinho vazio", size=14,
                                color=th.muted(page),
                                weight=ft.FontWeight.W_500),
                        ft.Text("Arraste produtos ou use a busca à esquerda",
                                size=10, color=th.muted(page)),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                       spacing=6),
                    alignment=ft.Alignment(0, 0),
                    height=180,
                )
            ]
            return

        total_items = sum(item.quantidade for item in self._carrinho)
        total       = sum(item.subtotal for item in self._carrinho)
        rows        = []

        for i, item in enumerate(self._carrinho):
            color = _avatar_color(item.id_produto)
            rows.append(ft.Container(
                content=ft.Row([
                    ft.Container(
                        ft.Text(str(i + 1), size=9, color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER),
                        bgcolor=color, border_radius=4,
                        padding=ft.padding.symmetric(horizontal=4, vertical=2),
                        width=20, alignment=ft.Alignment(0, 0),
                    ),
                    ft.Text(item.nome, size=12, color=th.text(page),
                            expand=True, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"×{item.quantidade}", size=11,
                            color=th.muted(page), width=26),
                    ft.Text(f"R$ {item.subtotal:.2f}", size=12,
                            color=th.accent(page), weight=ft.FontWeight.W_600,
                            width=70, text_align=ft.TextAlign.RIGHT),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=13,
                        icon_color=th.danger(page),
                        on_click=lambda e, it=item: self._remove_item(it),
                        style=ft.ButtonStyle(
                            shape=ft.CircleBorder(), padding=2
                        ),
                        tooltip="Remover item",
                    ),
                ], spacing=4,
                   vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.with_opacity(0.05, th.primary(page)),
                border_radius=6,
                padding=ft.padding.symmetric(horizontal=8, vertical=5),
                margin=ft.margin.only(bottom=3),
            ))

        rows.append(ft.Container(
            content=ft.Column([
                ft.Divider(color=th.border(page), height=1),
                ft.Container(height=4),
                ft.Row([
                    ft.Column([
                        ft.Text(
                            f"{len(self._carrinho)} produto{'s' if len(self._carrinho) != 1 else ''}",
                            size=10, color=th.muted(page),
                        ),
                        ft.Text(
                            f"{total_items} unidade{'s' if total_items != 1 else ''}",
                            size=10, color=th.muted(page),
                        ),
                    ], spacing=1, tight=True),
                    ft.Column([
                        ft.Text("Total", size=11, color=th.muted(page),
                                text_align=ft.TextAlign.RIGHT),
                        ft.Text(f"R$ {total:.2f}", size=18,
                                weight=ft.FontWeight.BOLD,
                                color=th.success(page),
                                text_align=ft.TextAlign.RIGHT),
                    ], spacing=1, tight=True,
                       horizontal_alignment=ft.CrossAxisAlignment.END),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                   vertical_alignment=ft.CrossAxisAlignment.END),
            ], spacing=0),
            padding=ft.padding.only(top=6),
        ))

        self._cart_ref.controls = rows

import flet as ft

from app.flet.controller import PageController
from app.flet import theme as th


from app.shared.ui_helpers import avatar_color as _palette_color, initials as _initials

_CARGOS = ["Supervisor", "Operador", "Caixa"]

_COR_OPCOES = [
    "#7C6FCD", "#00C9A7", "#FF6B6B", "#FFB700",
    "#4ECDC4", "#45B7D1", "#A29BFE", "#FD79A8",
    "#E84393", "#6C5CE7", "#0984E3", "#00B894",
]


class CadastrosPage:

    def __init__(self, ctrl: PageController, produto_repo, cliente_repo, operador_repo):
        self._ctrl = ctrl
        self._produto_repo = produto_repo
        self._cliente_repo = cliente_repo
        self._operador_repo = operador_repo
        self._tab_index = 0

    def show(self) -> None:
        async def _render_async():
            try:
                self._render()
            except Exception as ex:
                self._ctrl.notify(f"Erro ao renderizar cadastros: {ex}", ok=False)
        self._ctrl.page.run_task(_render_async)

    def _render(self) -> None:
        page = self._ctrl.page

        tabs = ft.Tabs(
            length=3,
            selected_index=self._tab_index,
            on_change=self._on_tab_change,
            animation_duration=200,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Produtos",   icon=ft.Icons.INVENTORY_2),
                            ft.Tab(label="Clientes",   icon=ft.Icons.PEOPLE),
                            ft.Tab(label="Operadores", icon=ft.Icons.BADGE),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            self._build_produtos(page),
                            self._build_clientes(page),
                            self._build_operadores(page),
                        ],
                    ),
                ],
            ),
        )

        self._ctrl.set_content(
            ft.Column([
                self._build_header(page),
                ft.Container(height=4),
                tabs,
            ], spacing=0, expand=True),
        )

    def _on_tab_change(self, e):
        self._tab_index = e.control.selected_index
        self._render()

    def _build_header(self, page: ft.Page) -> ft.Row:
        return ft.Row([
            ft.Container(
                ft.Icon(ft.Icons.EDIT_NOTE, size=16, color=th.primary(page)),
                bgcolor=ft.Colors.with_opacity(0.12, th.primary(page)),
                border_radius=8, padding=8,
            ),
            ft.Column([
                ft.Text("Cadastros", size=20, weight=ft.FontWeight.BOLD,
                        color=th.text(page)),
                ft.Text("Gerencie produtos, clientes e operadores",
                        size=12, color=th.muted(page)),
            ], spacing=2, tight=True),
        ], spacing=12)

    # ── Produtos ─────────────────────────────────────────────────

    def _build_produtos(self, page: ft.Page) -> ft.Column:
        produtos = self._produto_repo.todos()
        produtos.sort(key=lambda p: p.id_produto)

        rows = []
        for p in produtos:
            color = _palette_color(p.id_produto)
            rows.append(self._produto_row(page, p, color))

        add_btn = ft.ElevatedButton(
            "Adicionar Produto",
            icon=ft.Icons.ADD,
            on_click=lambda e: self._form_produto(page),
            style=ft.ButtonStyle(
                bgcolor=th.primary(page), color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=th.RADIUS_BTN),
                padding=ft.Padding(left=20, top=12, right=20, bottom=12),
            ),
        )

        return self._ctrl.make_card(
            ft.Column([
                ft.Row([
                    ft.Text(f"{len(produtos)} produtos cadastrados", size=13,
                            weight=ft.FontWeight.W_500, color=th.text(page)),
                    ft.Container(expand=True),
                    add_btn,
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(color=th.border(page)),
                ft.Column(rows, spacing=4) if rows else ft.Container(
                    ft.Text("Nenhum produto cadastrado.", size=13,
                            color=th.muted(page)),
                    padding=ft.Padding(left=24, top=24, right=24, bottom=24),
                ),
            ], spacing=10),
            padding=18,
        )

    def _produto_row(self, page, p, color):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    ft.Text(_initials(p.nome), size=11,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER),
                    bgcolor=color,
                    border_radius=50,
                    width=36, height=36,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    ft.Text(f"#{p.id_produto}", size=10,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD),
                    bgcolor=color, border_radius=4,
                    padding=ft.Padding(left=5, top=2, right=5, bottom=2),
                    width=36,
                ),
                ft.Text(p.nome, size=13, color=th.text(page), expand=True,
                        weight=ft.FontWeight.W_500),
                ft.Text(f"R$ {p.preco:.2f}", size=13,
                        color=th.accent(page), width=90,
                        weight=ft.FontWeight.W_600),
                ft.Text(f"Estoque: {p.quantidade}", size=12,
                        color=th.muted(page), width=90),
                ft.IconButton(
                    ft.Icons.EDIT, icon_size=16, icon_color=th.primary(page),
                    tooltip="Editar",
                    on_click=lambda e, prod=p: self._form_produto(page, prod),
                ),
                ft.IconButton(
                    ft.Icons.DELETE, icon_size=16, icon_color=th.danger(page),
                    tooltip="Remover",
                    on_click=lambda e, prod=p: self._confirmar_remover(
                        page, "produto", prod.nome,
                        lambda: self._remover_produto(prod.id_produto),
                    ),
                ),
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=th.card(page),
            border_radius=10,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.12, color)),
            padding=ft.Padding(left=14, top=8, right=14, bottom=8),
        )

    def _form_produto(self, page, produto=None):
        editing = produto is not None
        tf_nome = self._ctrl.make_text_field("Nome", "Ex: Arroz Integral 1kg")
        tf_qtd  = self._ctrl.make_text_field("Quantidade", "Ex: 50", ft.KeyboardType.NUMBER)
        tf_preco = self._ctrl.make_text_field("Preço (R$)", "Ex: 8.99", ft.KeyboardType.NUMBER)

        if editing:
            tf_nome.value = produto.nome
            tf_qtd.value  = str(produto.quantidade)
            tf_preco.value = f"{produto.preco:.2f}"

        def _save(e):
            nome = tf_nome.value.strip()
            if len(nome) < 2:
                self._ctrl.notify("Nome deve ter ao menos 2 caracteres.", ok=False)
                return
            try:
                qtd = int(tf_qtd.value.strip())
                preco = float(tf_preco.value.strip().replace(",", "."))
            except ValueError:
                self._ctrl.notify("Quantidade e preço devem ser numéricos.", ok=False)
                return
            if qtd < 0 or preco < 0:
                self._ctrl.notify("Valores não podem ser negativos.", ok=False)
                return

            try:
                if editing:
                    self._produto_repo.atualizar(produto.id_produto, nome, qtd, preco)
                    self._ctrl.notify(f"Produto '{nome}' atualizado.")
                else:
                    self._produto_repo.cadastrar(nome, qtd, preco)
                    self._ctrl.notify(f"Produto '{nome}' cadastrado.")
                self._ctrl.close_dialog()
                self._render()
            except RuntimeError as ex:
                self._ctrl.notify(str(ex), ok=False)

        titulo = "Editar Produto" if editing else "Novo Produto"
        self._show_form_dialog(page, titulo, ft.Icons.INVENTORY_2,
                               [tf_nome, tf_qtd, tf_preco], _save)

    def _remover_produto(self, id_produto: int):
        try:
            self._produto_repo.remover(id_produto)
            self._ctrl.notify("Produto removido.")
            self._render()
        except RuntimeError as ex:
            msg = str(ex)
            if "foreign key" in msg.lower() or "constraint" in msg.lower():
                self._ctrl.notify("Produto possui compras associadas e não pode ser removido.", ok=False)
            else:
                self._ctrl.notify(msg, ok=False)

    # ── Clientes ─────────────────────────────────────────────────

    def _build_clientes(self, page: ft.Page) -> ft.Column:
        clientes = self._cliente_repo.todos()
        clientes.sort(key=lambda c: c.id_cliente)

        rows = []
        for c in clientes:
            color = _palette_color(c.id_cliente)
            rows.append(self._cliente_row(page, c, color))

        add_btn = ft.ElevatedButton(
            "Adicionar Cliente",
            icon=ft.Icons.PERSON_ADD,
            on_click=lambda e: self._form_cliente(page),
            style=ft.ButtonStyle(
                bgcolor=th.primary(page), color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=th.RADIUS_BTN),
                padding=ft.Padding(left=20, top=12, right=20, bottom=12),
            ),
        )

        return self._ctrl.make_card(
            ft.Column([
                ft.Row([
                    ft.Text(f"{len(clientes)} clientes cadastrados", size=13,
                            weight=ft.FontWeight.W_500, color=th.text(page)),
                    ft.Container(expand=True),
                    add_btn,
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(color=th.border(page)),
                ft.Column(rows, spacing=4) if rows else ft.Container(
                    ft.Text("Nenhum cliente cadastrado.", size=13,
                            color=th.muted(page)),
                    padding=ft.Padding(left=24, top=24, right=24, bottom=24),
                ),
            ], spacing=10),
            padding=18,
        )

    def _cliente_row(self, page, c, color):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    ft.Text(_initials(c.nome), size=11,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER),
                    bgcolor=color,
                    border_radius=50,
                    width=36, height=36,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    ft.Text(f"#{c.id_cliente}", size=10,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD),
                    bgcolor=color, border_radius=4,
                    padding=ft.Padding(left=5, top=2, right=5, bottom=2),
                    width=36,
                ),
                ft.Text(c.nome, size=13, color=th.text(page), expand=True,
                        weight=ft.FontWeight.W_500),
                ft.IconButton(
                    ft.Icons.EDIT, icon_size=16, icon_color=th.primary(page),
                    tooltip="Editar",
                    on_click=lambda e, cl=c: self._form_cliente(page, cl),
                ),
                ft.IconButton(
                    ft.Icons.DELETE, icon_size=16, icon_color=th.danger(page),
                    tooltip="Remover",
                    on_click=lambda e, cl=c: self._confirmar_remover(
                        page, "cliente", cl.nome,
                        lambda: self._remover_cliente(cl.id_cliente),
                    ),
                ),
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=th.card(page),
            border_radius=10,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.12, color)),
            padding=ft.Padding(left=14, top=8, right=14, bottom=8),
        )

    def _form_cliente(self, page, cliente=None):
        editing = cliente is not None
        tf_nome = self._ctrl.make_text_field("Nome", "Ex: João Silva")

        if editing:
            tf_nome.value = cliente.nome

        def _save(e):
            nome = tf_nome.value.strip()
            if len(nome) < 3:
                self._ctrl.notify("Nome deve ter ao menos 3 caracteres.", ok=False)
                return
            try:
                if editing:
                    self._cliente_repo.atualizar(cliente.id_cliente, nome)
                    self._ctrl.notify(f"Cliente '{nome}' atualizado.")
                else:
                    self._cliente_repo.cadastrar(nome)
                    self._ctrl.notify(f"Cliente '{nome}' cadastrado.")
                self._ctrl.close_dialog()
                self._render()
            except RuntimeError as ex:
                self._ctrl.notify(str(ex), ok=False)

        titulo = "Editar Cliente" if editing else "Novo Cliente"
        self._show_form_dialog(page, titulo, ft.Icons.PERSON, [tf_nome], _save)

    def _remover_cliente(self, id_cliente: int):
        try:
            self._cliente_repo.remover(id_cliente)
            self._ctrl.notify("Cliente removido.")
            self._render()
        except RuntimeError as ex:
            msg = str(ex)
            if "foreign key" in msg.lower() or "constraint" in msg.lower():
                self._ctrl.notify("Cliente possui compras associadas e não pode ser removido.", ok=False)
            else:
                self._ctrl.notify(msg, ok=False)

    # ── Operadores ───────────────────────────────────────────────

    def _build_operadores(self, page: ft.Page) -> ft.Column:
        operadores = self._operador_repo.todos()

        rows = []
        for op in operadores:
            rows.append(self._operador_row(page, op))

        add_btn = ft.ElevatedButton(
            "Adicionar Operador",
            icon=ft.Icons.PERSON_ADD,
            on_click=lambda e: self._form_operador(page),
            style=ft.ButtonStyle(
                bgcolor=th.primary(page), color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=th.RADIUS_BTN),
                padding=ft.Padding(left=20, top=12, right=20, bottom=12),
            ),
        )

        return self._ctrl.make_card(
            ft.Column([
                ft.Row([
                    ft.Text(f"{len(operadores)} operadores cadastrados", size=13,
                            weight=ft.FontWeight.W_500, color=th.text(page)),
                    ft.Container(expand=True),
                    add_btn,
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(color=th.border(page)),
                ft.Column(rows, spacing=4) if rows else ft.Container(
                    ft.Text("Nenhum operador cadastrado.", size=13,
                            color=th.muted(page)),
                    padding=ft.Padding(left=24, top=24, right=24, bottom=24),
                ),
            ], spacing=10),
            padding=18,
        )

    def _operador_row(self, page, op):
        cargo_color = {
            "Supervisor": "#7C6FCD",
            "Operador":   th.primary(page),
            "Caixa":      "#FFB700",
        }.get(op.cargo, th.muted(page))

        return ft.Container(
            content=ft.Row([
                ft.Container(
                    ft.Text(op.iniciais, size=13,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER),
                    bgcolor=op.cor,
                    border_radius=50,
                    width=40, height=40,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    ft.Text(f"#{op.id_operador}", size=10,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD),
                    bgcolor=op.cor, border_radius=4,
                    padding=ft.Padding(left=5, top=2, right=5, bottom=2),
                    width=36,
                ),
                ft.Text(op.nome, size=13, color=th.text(page), expand=True,
                        weight=ft.FontWeight.W_500),
                ft.Container(
                    ft.Text(op.cargo, size=10, color=cargo_color,
                            weight=ft.FontWeight.W_600),
                    border=ft.Border.all(1, cargo_color),
                    border_radius=4,
                    padding=ft.Padding(left=8, top=3, right=8, bottom=3),
                    width=80,
                ),
                ft.IconButton(
                    ft.Icons.EDIT, icon_size=16, icon_color=th.primary(page),
                    tooltip="Editar",
                    on_click=lambda e, o=op: self._form_operador(page, o),
                ),
                ft.IconButton(
                    ft.Icons.DELETE, icon_size=16, icon_color=th.danger(page),
                    tooltip="Remover",
                    on_click=lambda e, o=op: self._confirmar_remover(
                        page, "operador", o.nome,
                        lambda: self._remover_operador(o.id_operador),
                    ),
                ),
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=th.card(page),
            border_radius=10,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.15, op.cor)),
            padding=ft.Padding(left=14, top=8, right=14, bottom=8),
        )

    def _form_operador(self, page, operador=None):
        editing = operador is not None
        tf_nome = self._ctrl.make_text_field("Nome", "Ex: João Silva")
        dd_cargo = ft.Dropdown(
            label="Cargo",
            options=[ft.DropdownOption(c) for c in _CARGOS],
            border_radius=th.RADIUS_INPUT,
            border_color=th.border(page),
            focused_border_color=th.primary(page),
            label_style=ft.TextStyle(color=th.muted(page)),
            text_style=ft.TextStyle(color=th.text(page)),
            bgcolor=th.surface(page),
            fill_color=th.surface(page),
            filled=True,
        )

        cor_selecionada = [operador.cor if editing else _COR_OPCOES[0]]

        def _build_color_row():
            circles = []
            for c in _COR_OPCOES:
                is_selected = c == cor_selecionada[0]
                circles.append(ft.Container(
                    content=ft.Icon(ft.Icons.CHECK, size=14, color=ft.Colors.WHITE)
                    if is_selected else None,
                    bgcolor=c,
                    border_radius=50,
                    width=28, height=28,
                    alignment=ft.Alignment(0, 0),
                    border=ft.Border.all(2, ft.Colors.WHITE) if is_selected else None,
                    on_click=lambda e, cor=c: _select_color(cor),
                ))
            return ft.Row(circles, spacing=6, wrap=True)

        color_row_container = ft.Container(content=_build_color_row())

        def _select_color(cor):
            cor_selecionada[0] = cor
            color_row_container.content = _build_color_row()
            page.update()

        if editing:
            tf_nome.value = operador.nome
            dd_cargo.value = operador.cargo

        def _save(e):
            nome = tf_nome.value.strip()
            if len(nome) < 3:
                self._ctrl.notify("Nome deve ter ao menos 3 caracteres.", ok=False)
                return
            cargo = dd_cargo.value
            if not cargo:
                self._ctrl.notify("Selecione um cargo.", ok=False)
                return

            iniciais = _initials(nome)
            cor = cor_selecionada[0]

            try:
                if editing:
                    self._operador_repo.atualizar(
                        operador.id_operador, nome, cargo, iniciais, cor)
                    self._ctrl.notify(f"Operador '{nome}' atualizado.")
                else:
                    self._operador_repo.cadastrar(nome, cargo, iniciais, cor)
                    self._ctrl.notify(f"Operador '{nome}' cadastrado.")
                self._ctrl.close_dialog()
                self._render()
            except RuntimeError as ex:
                self._ctrl.notify(str(ex), ok=False)

        titulo = "Editar Operador" if editing else "Novo Operador"
        fields = [
            tf_nome,
            dd_cargo,
            ft.Text("Cor do avatar", size=12, color=th.muted(page)),
            color_row_container,
        ]
        self._show_form_dialog(page, titulo, ft.Icons.BADGE, fields, _save)

    def _remover_operador(self, id_operador: int):
        try:
            self._operador_repo.remover(id_operador)
            self._ctrl.notify("Operador removido.")
            self._render()
        except RuntimeError as ex:
            msg = str(ex)
            if "foreign key" in msg.lower() or "constraint" in msg.lower():
                self._ctrl.notify("Operador possui compras associadas e não pode ser removido.", ok=False)
            else:
                self._ctrl.notify(msg, ok=False)

    # ── Dialogs compartilhados ───────────────────────────────────

    def _show_form_dialog(self, page, titulo, icon, fields, on_save):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Container(
                    ft.Icon(icon, size=16, color=ft.Colors.WHITE),
                    bgcolor=th.primary(page),
                    border_radius=8,
                    width=34, height=34, alignment=ft.Alignment(0, 0),
                ),
                ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD,
                        color=th.text(page)),
            ], spacing=10),
            content=ft.Container(
                content=ft.Column(fields, spacing=12, tight=True, width=380),
                padding=ft.Padding(top=8, bottom=4),
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: self._ctrl.close_dialog(),
                    style=ft.ButtonStyle(color=th.muted(page)),
                ),
                ft.ElevatedButton(
                    "Salvar",
                    icon=ft.Icons.SAVE,
                    on_click=on_save,
                    style=ft.ButtonStyle(
                        bgcolor=th.primary(page), color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=th.RADIUS_BTN),
                        padding=ft.Padding(left=20, top=12, right=20, bottom=12),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            bgcolor=th.surface(page),
            shape=ft.RoundedRectangleBorder(radius=th.RADIUS_CARD),
        )
        self._ctrl.show_dialog(dialog)

    def _confirmar_remover(self, page, tipo, nome, on_confirm):
        def _yes(e):
            self._ctrl.close_dialog()
            on_confirm()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER, color=th.danger(page), size=20),
                ft.Text(f"Remover {tipo}", size=16, weight=ft.FontWeight.BOLD,
                        color=th.text(page)),
            ], spacing=10),
            content=ft.Container(
                ft.Column([
                    ft.Text(f"Tem certeza que deseja remover '{nome}'?",
                            size=13, color=th.text(page)),
                    ft.Text("Esta ação não pode ser desfeita.",
                            size=12, color=th.muted(page)),
                ], spacing=6, tight=True, width=340),
                padding=ft.Padding(top=4, bottom=4),
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: self._ctrl.close_dialog(),
                    style=ft.ButtonStyle(color=th.muted(page)),
                ),
                ft.ElevatedButton(
                    "Remover",
                    icon=ft.Icons.DELETE,
                    on_click=_yes,
                    style=ft.ButtonStyle(
                        bgcolor=th.danger(page), color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=th.RADIUS_BTN),
                        padding=ft.Padding(left=20, top=12, right=20, bottom=12),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            bgcolor=th.surface(page),
            shape=ft.RoundedRectangleBorder(radius=th.RADIUS_CARD),
        )
        self._ctrl.show_dialog(dialog)

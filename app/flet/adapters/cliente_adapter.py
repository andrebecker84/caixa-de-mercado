import flet as ft
from app.core.ports import ClientePort
from app.flet.controller import PageController
from app.flet.bridge import InputBridge
from app.flet import theme as th

class ClienteFletAdapter(ClientePort):
    def __init__(self, ctrl: PageController):
        self._ctrl = ctrl
        self._bridge = InputBridge()

    def pedir_id(self) -> int:
        self._ctrl.set_content(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.PERSON_SEARCH, color=th.primary(self._ctrl.page), size=32),
                    ft.Text("Identificar Cliente", size=24, weight=ft.FontWeight.BOLD),
                ], spacing=15),
                ft.Column([
                    ft.Text("Insira o ID do cliente ou use '0' para continuar sem CPF.", size=14, color=th.muted(self._ctrl.page)),
                    id_field := self._ctrl.make_text_field("ID do Cliente", "Ex: 1, 2...", keyboard_type=ft.KeyboardType.NUMBER),
                    self._ctrl.make_primary_btn("Avançar", lambda _: self._on_id_selected(id_field.value)),
                ], spacing=15, width=400)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=30)
        )
        return int(self._bridge.wait() or 0)

    def _on_id_selected(self, val):
        self._bridge.resolve(int(val) if val.isdigit() else 0)

    def pedir_nome(self) -> str:
        self._ctrl.append_content(
            ft.Column([
                ft.Text("Cliente não encontrado. Gostaria de cadastrá-lo?", size=14, color=th.muted(self._ctrl.page)),
                nome_field := self._ctrl.make_text_field("Nome do Novo Cliente", "Ex: João Silva..."),
                self._ctrl.make_primary_btn("Cadastrar", lambda _: self._bridge.resolve(nome_field.value)),
            ], spacing=15, width=400)
        )
        return self._bridge.wait()

    def pedir_confirmacao_cadastro(self) -> bool:
        # Padrão: se inseriu nome, já confirma. 
        # Mas para ser literal com a porta:
        return True

    def exibir_nome_invalido(self, mensagem: str) -> None:
        self._ctrl.notify(mensagem, ok=False)

    def exibir_cliente_ja_cadastrado(self, nome: str, id_cliente: int) -> None:
        self._ctrl.notify(f"Cliente {nome} já identificado.", ok=True)

    def exibir_cliente_registrado(self, nome: str, id_cliente: int) -> None:
        self._ctrl.notify(f"Cliente {nome} cadastrado e pronto para a venda.", ok=True)

    def exibir_erro(self, mensagem: str) -> None:
        self._ctrl.notify(f"Erro no cliente: {mensagem}", ok=False)

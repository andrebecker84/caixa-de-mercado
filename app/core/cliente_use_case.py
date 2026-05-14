from app.core.ports import ClientePort
from app.domain.models import Cliente
from app.domain.repositories.cliente_repository import ClienteRepository
from app.domain.validators.nome_validator import ValidadorNome


class ClienteUseCase:

    def __init__(
        self,
        cliente_repo: ClienteRepository,
        porta: ClientePort,
        validador: ValidadorNome | None = None,
    ):
        self._repo = cliente_repo
        self._porta = porta
        self._validador = validador or ValidadorNome()

    def validar_ou_cadastrar(self) -> Cliente | None:
        try:
            id_cliente = self._porta.pedir_id()
            cliente = self._repo.buscar_por_id(id_cliente)
            if cliente:
                return cliente
            if self._porta.pedir_confirmacao_cadastro():
                return self._cadastrar()
            return None
        except Exception as e:
            self._porta.exibir_erro(str(e))
            return None

    def listar(self) -> list[Cliente]:
        return self._repo.todos()

    def _cadastrar(self) -> Cliente | None:
        while True:
            nome = self._porta.pedir_nome()
            valido, mensagem = self._validador.validar(nome)
            if not valido:
                self._porta.exibir_nome_invalido(mensagem)
                continue

            existente = self._repo.buscar_por_nome(nome)
            if existente:
                self._porta.exibir_cliente_ja_cadastrado(nome, existente.id_cliente)
                continue

            try:
                cliente = self._repo.cadastrar(nome)
                self._porta.exibir_cliente_registrado(cliente.nome, cliente.id_cliente)
                return cliente
            except RuntimeError as e:
                self._porta.exibir_erro(str(e))
                return None

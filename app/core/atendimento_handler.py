from app.core.atendimento_use_case import AtendimentoUseCase
from app.core.cliente_use_case import ClienteUseCase
from app.core.comando import Comando
from app.infrastructure.repositories.cliente_repository import SQLAlchemyClienteRepository
from app.infrastructure.repositories.compra_repository import SQLAlchemyCompraRepository
from app.infrastructure.repositories.produto_repository import SQLAlchemyProdutoRepository
from app.views.atendimento_adapter import AtendimentoTerminalAdapter
from app.views.cliente_adapter import ClienteTerminalAdapter
from app.views.sistema_view import exibir_cancelamento


class AtendimentoHandler(Comando):

    def __init__(self, sessao):
        self._sessao = sessao

    def executar(self) -> None:
        cliente_repo = SQLAlchemyClienteRepository(self._sessao)
        produto_repo = SQLAlchemyProdutoRepository(self._sessao)
        compra_repo = SQLAlchemyCompraRepository(self._sessao)

        cliente = ClienteUseCase(cliente_repo, ClienteTerminalAdapter()).validar_ou_cadastrar()
        if not cliente:
            exibir_cancelamento()
            return

        AtendimentoUseCase(
            produto_repo, compra_repo, AtendimentoTerminalAdapter()
        ).atender(cliente.nome, cliente.id_cliente)

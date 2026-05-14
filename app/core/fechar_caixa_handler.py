from app.core.caixa_use_case import CaixaUseCase
from app.core.comando import Comando
from app.infrastructure.repositories.compra_repository import SQLAlchemyCompraRepository
from app.infrastructure.repositories.produto_repository import SQLAlchemyProdutoRepository
from app.views.caixa_adapter import CaixaTerminalAdapter


class FecharCaixaHandler(Comando):

    def __init__(self, sessao):
        self._sessao = sessao

    def executar(self) -> None:
        compra_repo = SQLAlchemyCompraRepository(self._sessao)
        produto_repo = SQLAlchemyProdutoRepository(self._sessao)
        CaixaUseCase(compra_repo, produto_repo, CaixaTerminalAdapter()).fechar()

from app.core.ports import CaixaPort
from app.domain.repositories.compra_repository import CompraRepository
from app.domain.repositories.produto_repository import ProdutoRepository


class CaixaUseCase:

    def __init__(
        self,
        compra_repo: CompraRepository,
        produto_repo: ProdutoRepository,
        porta: CaixaPort,
    ):
        self._compra_repo = compra_repo
        self._produto_repo = produto_repo
        self._porta = porta

    def fechar(self) -> None:
        self._porta.exibir_fechamento_inicio()

        compras = self._compra_repo.totais_do_dia()
        if compras:
            self._porta.exibir_fechamento_compras(compras)
        else:
            self._porta.exibir_fechamento_vazio()

        sem_estoque = self._produto_repo.sem_estoque()
        disponiveis = self._produto_repo.listar_para_estoque()
        self._porta.verificar_estoque(sem_estoque, disponiveis)

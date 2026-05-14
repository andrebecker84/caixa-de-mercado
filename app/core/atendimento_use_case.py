from decimal import Decimal

from app.core.ports import AtendimentoPort
from app.domain.models import ItemCarrinho
from app.domain.repositories.compra_repository import CompraRepository
from app.domain.repositories.produto_repository import ProdutoRepository


class AtendimentoUseCase:

    def __init__(
        self,
        produto_repo: ProdutoRepository,
        compra_repo: CompraRepository,
        porta: AtendimentoPort,
    ):
        self._produto_repo = produto_repo
        self._compra_repo = compra_repo
        self._porta = porta

    def atender(
        self,
        cliente_nome: str,
        cliente_id: int,
        id_operador: int | None = None,
        token: str | None = None,
    ) -> tuple:
        self._porta.exibir_inicio(cliente_nome)

        try:
            produtos = self._produto_repo.disponiveis()
        except RuntimeError as e:
            self._porta.exibir_erro(str(e))
            return [], Decimal("0.0"), []

        if not produtos:
            self._porta.exibir_erro("Nenhum produto disponível.")
            return [], Decimal("0.0"), []

        self._porta.exibir_produtos(produtos)

        carrinho: list[ItemCarrinho] = []
        cancelados: list[ItemCarrinho] = []
        total = Decimal("0.0")

        while True:
            id_produto = self._porta.pedir_id_produto()
            if id_produto == 0:
                break
            try:
                total += self._processar_item(id_produto, carrinho, cancelados)
            except (RuntimeError, ValueError) as e:
                self._porta.exibir_erro(str(e))

        if not carrinho:
            return [], Decimal("0.0"), cancelados

        while True:
            total = sum(item.subtotal for item in carrinho)
            self._porta.exibir_carrinho(cliente_nome, carrinho, cancelados, total)
            result = self._porta.confirmar_compra()

            if result == 2:  # adicionar mais
                while True:
                    id_produto = self._porta.pedir_id_produto()
                    if id_produto == 0:
                        break
                    try:
                        total += self._processar_item(id_produto, carrinho, cancelados)
                    except (RuntimeError, ValueError) as e:
                        self._porta.exibir_erro(str(e))
                continue

            if not result:  # cancelar
                self._porta.exibir_compra_cancelada()
                self._liberar_carrinho(carrinho)
                return [], Decimal("0.0"), carrinho + cancelados

            break  # confirmar

        try:
            id_compra = self._compra_repo.registrar(cliente_id, carrinho, id_operador, token)
            self._porta.exibir_compra_registrada(id_compra)
        except RuntimeError as e:
            self._porta.exibir_erro(str(e))
            self._liberar_carrinho(carrinho)
            return [], Decimal("0.0"), carrinho + cancelados

        return carrinho, total, cancelados

    def _processar_item(
        self,
        id_produto: int,
        carrinho: list[ItemCarrinho],
        cancelados: list[ItemCarrinho],
    ) -> Decimal:
        produto = self._produto_repo.buscar_por_id(id_produto)
        if not produto or produto.quantidade == 0:
            raise ValueError("Produto não encontrado ou sem estoque.")

        quantidade = self._porta.pedir_quantidade(produto.nome)
        if not (0 < quantidade <= produto.quantidade):
            raise ValueError("Quantidade inválida ou superior ao estoque disponível.")

        item = ItemCarrinho(produto.id_produto, produto.nome, quantidade, produto.preco)

        if not self._porta.confirmar_adicao(produto.nome, quantidade):
            cancelados.append(item)
            self._porta.exibir_item_nao_adicionado(produto.nome)
            return Decimal("0.0")

        self._produto_repo.reservar(id_produto, quantidade)
        carrinho.append(item)
        self._porta.exibir_item_adicionado(produto.nome, list(carrinho))
        return item.subtotal

    def _liberar_carrinho(self, carrinho: list[ItemCarrinho]) -> None:
        for item in carrinho:
            try:
                self._produto_repo.liberar(item.id_produto, item.quantidade)
            except RuntimeError as err:
                self._porta.exibir_erro(f"Falha ao liberar estoque: {err}")

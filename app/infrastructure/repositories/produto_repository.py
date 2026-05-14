from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError

from app.domain.models import Produto
from app.domain.repositories.produto_repository import ProdutoRepository


class SQLAlchemyProdutoRepository(ProdutoRepository):

    def __init__(self, sessao):
        self._sessao = sessao

    def todos(self) -> list[Produto]:
        try:
            return self._sessao.query(Produto).all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Erro ao listar produtos: {e}")

    def disponiveis(self) -> list[Produto]:
        try:
            return self._sessao.query(Produto).filter(Produto.quantidade > 0).all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Erro ao listar produtos disponíveis: {e}")

    def sem_estoque(self) -> list[Produto]:
        try:
            return self._sessao.query(Produto).filter_by(quantidade=0).all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Erro ao buscar produtos sem estoque: {e}")

    def buscar_por_id(self, id_produto: int) -> Produto | None:
        try:
            return self._sessao.query(Produto).filter_by(id_produto=id_produto).first()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Erro ao buscar produto: {e}")

    def listar_para_estoque(self) -> list[Produto]:
        try:
            return self._sessao.query(Produto).filter(Produto.quantidade > 0).all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Erro ao listar estoque: {e}")

    def count(self) -> int:
        try:
            return self._sessao.query(Produto).count()
        except SQLAlchemyError:
            return 0

    def reservar(self, id_produto: int, quantidade: int) -> None:
        try:
            produto = self._sessao.get(Produto, id_produto)
            if produto is None:
                raise RuntimeError(f"Produto #{id_produto} não encontrado.")
            if produto.quantidade < quantidade:
                raise RuntimeError("Estoque insuficiente para reserva.")
            produto.quantidade -= quantidade
            self._sessao.commit()
        except SQLAlchemyError as e:
            self._sessao.rollback()
            raise RuntimeError(f"Erro ao reservar estoque: {e}")

    def liberar(self, id_produto: int, quantidade: int) -> None:
        try:
            produto = self._sessao.get(Produto, id_produto)
            if produto:
                produto.quantidade += quantidade
                self._sessao.commit()
        except SQLAlchemyError as e:
            self._sessao.rollback()
            raise RuntimeError(f"Erro ao liberar estoque: {e}")

    def cadastrar(self, nome: str, quantidade: int, preco: Decimal) -> Produto:
        try:
            produto = Produto(nome=nome, quantidade=quantidade, preco=preco)
            self._sessao.add(produto)
            self._sessao.commit()
            return produto
        except SQLAlchemyError as e:
            self._sessao.rollback()
            raise RuntimeError(f"Erro ao cadastrar produto: {e}")

    def atualizar(self, id_produto: int, nome: str, quantidade: int, preco: Decimal) -> Produto | None:
        try:
            produto = self._sessao.get(Produto, id_produto)
            if not produto:
                return None
            produto.nome = nome
            produto.quantidade = quantidade
            produto.preco = preco
            self._sessao.commit()
            return produto
        except SQLAlchemyError as e:
            self._sessao.rollback()
            raise RuntimeError(f"Erro ao atualizar produto: {e}")

    def remover(self, id_produto: int) -> None:
        try:
            produto = self._sessao.get(Produto, id_produto)
            if not produto:
                raise RuntimeError(f"Produto #{id_produto} não encontrado.")
            self._sessao.delete(produto)
            self._sessao.commit()
        except SQLAlchemyError as e:
            self._sessao.rollback()
            raise RuntimeError(f"Erro ao remover produto: {e}")

from sqlalchemy.exc import SQLAlchemyError

from app.domain.models import Cliente
from app.domain.repositories.cliente_repository import ClienteRepository


class SQLAlchemyClienteRepository(ClienteRepository):

    def __init__(self, sessao):
        self._sessao = sessao

    def todos(self) -> list[Cliente]:
        try:
            return self._sessao.query(Cliente).all()
        except SQLAlchemyError:
            return []

    def buscar_por_id(self, id_cliente: int) -> Cliente | None:
        try:
            return self._sessao.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
        except SQLAlchemyError:
            return None

    def count(self) -> int:
        try:
            return self._sessao.query(Cliente).count()
        except SQLAlchemyError:
            return 0

    def buscar_por_nome(self, nome: str) -> Cliente | None:
        try:
            return self._sessao.query(Cliente).filter(Cliente.nome == nome).first()
        except SQLAlchemyError:
            return None

    def cadastrar(self, nome: str) -> Cliente:
        try:
            cliente = Cliente(nome=nome)
            self._sessao.add(cliente)
            self._sessao.commit()
            return cliente
        except SQLAlchemyError as e:
            self._sessao.rollback()
            raise RuntimeError(f"Erro ao cadastrar cliente: {e}")

    def atualizar(self, id_cliente: int, nome: str) -> Cliente | None:
        try:
            cliente = self._sessao.get(Cliente, id_cliente)
            if not cliente:
                return None
            cliente.nome = nome
            self._sessao.commit()
            return cliente
        except SQLAlchemyError as e:
            self._sessao.rollback()
            raise RuntimeError(f"Erro ao atualizar cliente: {e}")

    def remover(self, id_cliente: int) -> None:
        try:
            cliente = self._sessao.get(Cliente, id_cliente)
            if not cliente:
                raise RuntimeError(f"Cliente #{id_cliente} não encontrado.")
            self._sessao.delete(cliente)
            self._sessao.commit()
        except SQLAlchemyError as e:
            self._sessao.rollback()
            raise RuntimeError(f"Erro ao remover cliente: {e}")

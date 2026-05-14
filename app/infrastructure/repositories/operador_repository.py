from sqlalchemy.exc import SQLAlchemyError

from app.domain.models import Operador
from app.domain.repositories.operador_repository import OperadorRepository


class SQLAlchemyOperadorRepository(OperadorRepository):

    def __init__(self, sessao):
        self._sessao = sessao

    def todos(self) -> list[Operador]:
        try:
            return self._sessao.query(Operador).order_by(Operador.id_operador).all()
        except SQLAlchemyError as e:
            self._sessao.rollback()
            raise RuntimeError(f"Erro ao listar operadores: {e}")

    def buscar_por_id(self, id_operador: int) -> Operador | None:
        try:
            return self._sessao.query(Operador).filter_by(id_operador=id_operador).first()
        except SQLAlchemyError as e:
            self._sessao.rollback()
            raise RuntimeError(f"Erro ao buscar operador: {e}")

    def count(self) -> int:
        try:
            return self._sessao.query(Operador).count()
        except SQLAlchemyError:
            self._sessao.rollback()
            return 0

    def cadastrar(self, nome: str, cargo: str, iniciais: str, cor: str) -> Operador:
        try:
            operador = Operador(nome=nome, cargo=cargo, iniciais=iniciais, cor=cor)
            self._sessao.add(operador)
            self._sessao.commit()
            return operador
        except SQLAlchemyError as e:
            self._sessao.rollback()
            raise RuntimeError(f"Erro ao cadastrar operador: {e}")

    def atualizar(self, id_operador: int, nome: str, cargo: str, iniciais: str, cor: str) -> Operador | None:
        try:
            operador = self._sessao.get(Operador, id_operador)
            if not operador:
                return None
            operador.nome = nome
            operador.cargo = cargo
            operador.iniciais = iniciais
            operador.cor = cor
            self._sessao.commit()
            return operador
        except SQLAlchemyError as e:
            self._sessao.rollback()
            raise RuntimeError(f"Erro ao atualizar operador: {e}")

    def remover(self, id_operador: int) -> None:
        try:
            operador = self._sessao.get(Operador, id_operador)
            if not operador:
                raise RuntimeError(f"Operador #{id_operador} não encontrado.")
            self._sessao.delete(operador)
            self._sessao.commit()
        except SQLAlchemyError as e:
            self._sessao.rollback()
            raise RuntimeError(f"Erro ao remover operador: {e}")

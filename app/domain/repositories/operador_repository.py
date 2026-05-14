from abc import ABC, abstractmethod

from app.domain.models import Operador


class OperadorRepository(ABC):

    @abstractmethod
    def todos(self) -> list[Operador]: ...

    @abstractmethod
    def buscar_por_id(self, id_operador: int) -> Operador | None: ...

    @abstractmethod
    def count(self) -> int: ...

    @abstractmethod
    def cadastrar(self, nome: str, cargo: str, iniciais: str, cor: str) -> Operador: ...

    @abstractmethod
    def atualizar(self, id_operador: int, nome: str, cargo: str, iniciais: str, cor: str) -> Operador | None: ...

    @abstractmethod
    def remover(self, id_operador: int) -> None: ...

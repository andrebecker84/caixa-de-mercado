from abc import ABC, abstractmethod

from app.domain.models import Cliente


class ClienteRepository(ABC):

    @abstractmethod
    def todos(self) -> list[Cliente]: ...

    @abstractmethod
    def buscar_por_id(self, id_cliente: int) -> Cliente | None: ...

    @abstractmethod
    def buscar_por_nome(self, nome: str) -> Cliente | None: ...

    @abstractmethod
    def count(self) -> int: ...

    @abstractmethod
    def cadastrar(self, nome: str) -> Cliente: ...

    @abstractmethod
    def atualizar(self, id_cliente: int, nome: str) -> Cliente | None: ...

    @abstractmethod
    def remover(self, id_cliente: int) -> None: ...

from abc import ABC, abstractmethod
from decimal import Decimal

from app.domain.models import Produto


class ProdutoRepository(ABC):

    @abstractmethod
    def todos(self) -> list[Produto]: ...

    @abstractmethod
    def disponiveis(self) -> list[Produto]: ...

    @abstractmethod
    def sem_estoque(self) -> list[Produto]: ...

    @abstractmethod
    def buscar_por_id(self, id_produto: int) -> Produto | None: ...

    @abstractmethod
    def listar_para_estoque(self) -> list[Produto]: ...

    @abstractmethod
    def count(self) -> int: ...

    @abstractmethod
    def reservar(self, id_produto: int, quantidade: int) -> None: ...

    @abstractmethod
    def liberar(self, id_produto: int, quantidade: int) -> None: ...

    @abstractmethod
    def cadastrar(self, nome: str, quantidade: int, preco: Decimal) -> Produto: ...

    @abstractmethod
    def atualizar(self, id_produto: int, nome: str, quantidade: int, preco: Decimal) -> Produto | None: ...

    @abstractmethod
    def remover(self, id_produto: int) -> None: ...

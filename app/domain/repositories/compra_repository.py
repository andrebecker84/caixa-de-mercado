from abc import ABC, abstractmethod

from app.domain.models import ItemCarrinho


class CompraRepository(ABC):

    @abstractmethod
    def registrar(self, id_cliente: int, itens: list[ItemCarrinho],
                  id_operador: int | None = None, token: str | None = None) -> int: ...

    @abstractmethod
    def totais_do_dia(self) -> list: ...

    @abstractmethod
    def total_do_dia(self) -> float: ...

    @abstractmethod
    def contagem_hoje(self) -> int: ...

    @abstractmethod
    def total_da_semana(self) -> float: ...

    @abstractmethod
    def total_do_mes(self) -> float: ...

    @abstractmethod
    def vendas_por_dia(self, dias: int) -> list[tuple]: ...

    @abstractmethod
    def top_produtos(self, limit: int) -> list[tuple]: ...

    @abstractmethod
    def melhor_operador_hoje(self) -> tuple | None: ...

    @abstractmethod
    def vendas_calendario_mes(self, ano: int, mes: int) -> dict: ...

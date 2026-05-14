from abc import ABC, abstractmethod
from decimal import Decimal

from app.domain.models import Produto


class AtendimentoPort(ABC):

    @abstractmethod
    def exibir_inicio(self, cliente_nome: str) -> None: ...

    @abstractmethod
    def exibir_produtos(self, produtos: list) -> None: ...

    @abstractmethod
    def pedir_id_produto(self) -> int: ...

    @abstractmethod
    def pedir_quantidade(self, nome: str) -> int: ...

    @abstractmethod
    def confirmar_adicao(self, nome: str, quantidade: int) -> bool: ...

    @abstractmethod
    def exibir_item_adicionado(self, nome: str, carrinho: list) -> None: ...

    @abstractmethod
    def exibir_item_nao_adicionado(self, nome: str) -> None: ...

    @abstractmethod
    def exibir_carrinho(self, cliente_nome: str, carrinho: list, cancelados: list, total: Decimal) -> None: ...

    @abstractmethod
    def confirmar_compra(self) -> int: ...

    @abstractmethod
    def exibir_compra_cancelada(self) -> None: ...

    @abstractmethod
    def exibir_compra_registrada(self, id_compra: int) -> None: ...

    @abstractmethod
    def exibir_erro(self, mensagem: str) -> None: ...


class ClientePort(ABC):

    @abstractmethod
    def pedir_id(self) -> int: ...

    @abstractmethod
    def pedir_nome(self) -> str: ...

    @abstractmethod
    def pedir_confirmacao_cadastro(self) -> bool: ...

    @abstractmethod
    def exibir_nome_invalido(self, mensagem: str) -> None: ...

    @abstractmethod
    def exibir_cliente_ja_cadastrado(self, nome: str, id_cliente: int) -> None: ...

    @abstractmethod
    def exibir_cliente_registrado(self, nome: str, id_cliente: int) -> None: ...

    @abstractmethod
    def exibir_erro(self, mensagem: str) -> None: ...


class CaixaPort(ABC):

    @abstractmethod
    def exibir_fechamento_inicio(self) -> None: ...

    @abstractmethod
    def exibir_fechamento_compras(self, compras: list) -> None: ...

    @abstractmethod
    def exibir_fechamento_vazio(self) -> None: ...

    @abstractmethod
    def verificar_estoque(self, sem_estoque: list[Produto], disponiveis: list[Produto]) -> None: ...

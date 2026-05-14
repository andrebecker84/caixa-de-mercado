from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import Column, DateTime, Integer, String, DECIMAL, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


@dataclass
class ItemCarrinho:
    id_produto: int
    nome: str
    quantidade: int
    preco_unitario: Decimal

    def __post_init__(self):
        if self.quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero.")
        if self.preco_unitario < Decimal("0"):
            raise ValueError("Preço unitário não pode ser negativo.")

    @property
    def subtotal(self) -> Decimal:
        return self.preco_unitario * self.quantidade


class Operador(Base):
    __tablename__ = 'operador'

    id_operador = Column(Integer, primary_key=True, autoincrement=True)
    nome        = Column(String(50), nullable=False)
    cargo       = Column(String(30), nullable=False)
    iniciais    = Column(String(4), nullable=False)
    cor         = Column(String(10), nullable=False)

    compras = relationship('Compra', back_populates='operador')

    @property
    def id(self) -> int:
        return self.id_operador


class Cliente(Base):
    __tablename__ = 'cliente'

    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), nullable=False)

    compras = relationship('Compra', back_populates='cliente')


class Produto(Base):
    __tablename__ = 'produto'

    id_produto = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco = Column(DECIMAL(10, 2), nullable=False)

    itens = relationship('Item', back_populates='produto')


class Compra(Base):
    __tablename__ = 'compra'

    id_compra    = Column(Integer, primary_key=True, autoincrement=True)
    data_compra  = Column(DateTime, nullable=False)
    id_cliente   = Column(Integer, ForeignKey('cliente.id_cliente'), nullable=False)
    id_operador  = Column(Integer, ForeignKey('operador.id_operador'), nullable=True)
    token_compra = Column(String(36), nullable=True)

    cliente  = relationship('Cliente', back_populates='compras')
    operador = relationship('Operador', back_populates='compras')
    itens    = relationship('Item', back_populates='compra')


class Item(Base):
    __tablename__ = 'item'

    id_item = Column(Integer, primary_key=True, autoincrement=True)
    quantidade = Column(Integer, nullable=False)
    id_compra = Column(Integer, ForeignKey('compra.id_compra'), nullable=False)
    id_produto = Column(Integer, ForeignKey('produto.id_produto'), nullable=False)

    compra = relationship('Compra', back_populates='itens')
    produto = relationship('Produto', back_populates='itens')

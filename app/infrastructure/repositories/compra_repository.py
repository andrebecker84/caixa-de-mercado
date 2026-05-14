import datetime

from sqlalchemy import func, cast, Date
from sqlalchemy.exc import SQLAlchemyError

from app.domain.models import Cliente, Compra, Item, ItemCarrinho, Produto
from app.domain.repositories.compra_repository import CompraRepository


class SQLAlchemyCompraRepository(CompraRepository):

    def __init__(self, sessao):
        self._sessao = sessao

    def registrar(self, id_cliente: int, itens: list[ItemCarrinho],
                  id_operador: int | None = None, token: str | None = None) -> int:
        try:
            nova_compra = Compra(
                data_compra=datetime.datetime.now(),
                id_cliente=id_cliente,
                id_operador=id_operador,
                token_compra=token,
            )
            self._sessao.add(nova_compra)
            self._sessao.flush()

            for item in itens:
                self._sessao.add(Item(
                    id_compra=nova_compra.id_compra,
                    id_produto=item.id_produto,
                    quantidade=item.quantidade,
                ))
            self._sessao.commit()
            return nova_compra.id_compra

        except SQLAlchemyError as e:
            self._sessao.rollback()
            raise RuntimeError(f"Erro ao registrar compra: {e}")

    def totais_do_dia(self) -> list:
        hoje = datetime.date.today()
        inicio = datetime.datetime.combine(hoje, datetime.time.min)
        fim = datetime.datetime.combine(hoje, datetime.time.max)
        try:
            return (
                self._sessao.query(
                    Cliente.nome,
                    func.sum(Produto.preco * Item.quantidade).label('total')
                )
                .join(Compra)
                .join(Item)
                .join(Produto)
                .filter(Compra.data_compra.between(inicio, fim))
                .group_by(Cliente.nome)
                .all()
            )
        except SQLAlchemyError:
            self._sessao.rollback()
            return []

    def total_do_dia(self) -> float:
        hoje = datetime.date.today()
        inicio = datetime.datetime.combine(hoje, datetime.time.min)
        fim = datetime.datetime.combine(hoje, datetime.time.max)
        try:
            result = (
                self._sessao.query(func.sum(Produto.preco * Item.quantidade))
                .join(Item, Item.id_produto == Produto.id_produto)
                .join(Compra, Compra.id_compra == Item.id_compra)
                .filter(Compra.data_compra.between(inicio, fim))
                .scalar()
            )
            return float(result or 0)
        except SQLAlchemyError:
            self._sessao.rollback()
            return 0.0

    def contagem_hoje(self) -> int:
        hoje = datetime.date.today()
        inicio = datetime.datetime.combine(hoje, datetime.time.min)
        fim = datetime.datetime.combine(hoje, datetime.time.max)
        try:
            return (
                self._sessao.query(func.count(Compra.id_compra))
                .filter(Compra.data_compra.between(inicio, fim))
                .scalar() or 0
            )
        except SQLAlchemyError:
            self._sessao.rollback()
            return 0

    def total_da_semana(self) -> float:
        inicio = datetime.datetime.combine(
            datetime.date.today() - datetime.timedelta(days=6), datetime.time.min
        )
        try:
            result = (
                self._sessao.query(func.sum(Produto.preco * Item.quantidade))
                .join(Item, Item.id_produto == Produto.id_produto)
                .join(Compra, Compra.id_compra == Item.id_compra)
                .filter(Compra.data_compra >= inicio)
                .scalar()
            )
            return float(result or 0)
        except SQLAlchemyError:
            self._sessao.rollback()
            return 0.0

    def total_do_mes(self) -> float:
        hoje = datetime.date.today()
        inicio = datetime.datetime(hoje.year, hoje.month, 1)
        try:
            result = (
                self._sessao.query(func.sum(Produto.preco * Item.quantidade))
                .join(Item, Item.id_produto == Produto.id_produto)
                .join(Compra, Compra.id_compra == Item.id_compra)
                .filter(Compra.data_compra >= inicio)
                .scalar()
            )
            return float(result or 0)
        except SQLAlchemyError:
            self._sessao.rollback()
            return 0.0

    def vendas_por_dia(self, dias: int) -> list[tuple]:
        inicio = datetime.datetime.combine(
            datetime.date.today() - datetime.timedelta(days=dias - 1), datetime.time.min
        )
        try:
            rows = (
                self._sessao.query(
                    cast(Compra.data_compra, Date).label('dia'),
                    func.sum(Produto.preco * Item.quantidade).label('total')
                )
                .join(Item, Item.id_compra == Compra.id_compra)
                .join(Produto, Produto.id_produto == Item.id_produto)
                .filter(Compra.data_compra >= inicio)
                .group_by(cast(Compra.data_compra, Date))
                .order_by(cast(Compra.data_compra, Date))
                .all()
            )
            return [(row.dia, float(row.total or 0)) for row in rows]
        except SQLAlchemyError:
            self._sessao.rollback()
            return []

    def top_produtos(self, limit: int = 5) -> list[tuple]:
        hoje = datetime.date.today()
        inicio = datetime.datetime(hoje.year, hoje.month, 1)
        try:
            rows = (
                self._sessao.query(
                    Produto.nome,
                    func.sum(Item.quantidade).label('qtd'),
                    func.sum(Produto.preco * Item.quantidade).label('total')
                )
                .join(Item, Item.id_produto == Produto.id_produto)
                .join(Compra, Compra.id_compra == Item.id_compra)
                .filter(Compra.data_compra >= inicio)
                .group_by(Produto.id_produto, Produto.nome)
                .order_by(func.sum(Item.quantidade).desc())
                .limit(limit)
                .all()
            )
            return [(r.nome, int(r.qtd), float(r.total or 0)) for r in rows]
        except SQLAlchemyError:
            self._sessao.rollback()
            return []

    def vendas_calendario_mes(self, ano: int, mes: int) -> dict:
        import calendar as _cal
        ultimo_dia = _cal.monthrange(ano, mes)[1]
        inicio = datetime.datetime(ano, mes, 1)
        fim    = datetime.datetime(ano, mes, ultimo_dia, 23, 59, 59)
        try:
            rows = (
                self._sessao.query(
                    func.day(Compra.data_compra).label('dia'),
                    func.count(Compra.id_compra).label('transacoes'),
                    func.sum(Produto.preco * Item.quantidade).label('total'),
                )
                .join(Item,    Item.id_compra  == Compra.id_compra)
                .join(Produto, Produto.id_produto == Item.id_produto)
                .filter(Compra.data_compra.between(inicio, fim))
                .group_by(func.day(Compra.data_compra))
                .all()
            )
            return {int(r.dia): {'total': float(r.total or 0), 'transacoes': int(r.transacoes)} for r in rows}
        except SQLAlchemyError:
            self._sessao.rollback()
            return {}

    def melhor_operador_hoje(self) -> tuple | None:
        hoje = datetime.date.today()
        inicio = datetime.datetime.combine(hoje, datetime.time.min)
        fim = datetime.datetime.combine(hoje, datetime.time.max)
        try:
            row = (
                self._sessao.query(
                    Compra.id_operador,
                    func.count(Compra.id_compra).label('vendas'),
                    func.sum(Produto.preco * Item.quantidade).label('total')
                )
                .join(Item, Item.id_compra == Compra.id_compra)
                .join(Produto, Produto.id_produto == Item.id_produto)
                .filter(
                    Compra.data_compra.between(inicio, fim),
                    Compra.id_operador.isnot(None)
                )
                .group_by(Compra.id_operador)
                .order_by(func.sum(Produto.preco * Item.quantidade).desc())
                .first()
            )
            if row:
                return (row.id_operador, int(row.vendas), float(row.total or 0))
            return None
        except SQLAlchemyError:
            self._sessao.rollback()
            return None

    def vendas_por_operador_no_dia(self, ano: int, mes: int, dia: int) -> list[tuple]:
        inicio = datetime.datetime(ano, mes, dia, 0, 0, 0)
        fim    = datetime.datetime(ano, mes, dia, 23, 59, 59)
        try:
            rows = (
                self._sessao.query(
                    Compra.id_operador,
                    func.count(Compra.id_compra).label('qtd_vendas'),
                    func.sum(Produto.preco * Item.quantidade).label('total')
                )
                .join(Item,    Item.id_compra    == Compra.id_compra)
                .join(Produto, Produto.id_produto == Item.id_produto)
                .filter(
                    Compra.data_compra.between(inicio, fim),
                    Compra.id_operador.isnot(None),
                )
                .group_by(Compra.id_operador)
                .order_by(func.sum(Produto.preco * Item.quantidade).desc())
                .all()
            )
            return [(r.id_operador, int(r.qtd_vendas), float(r.total or 0)) for r in rows]
        except SQLAlchemyError:
            self._sessao.rollback()
            return []

    def top_clientes(self, limite: int = 5) -> list[tuple]:
        hoje = datetime.date.today()
        inicio = datetime.datetime(hoje.year, hoje.month, 1)
        try:
            rows = (
                self._sessao.query(
                    Cliente.nome,
                    func.count(Compra.id_compra).label('qtd_compras'),
                    func.sum(Produto.preco * Item.quantidade).label('total_gasto')
                )
                .join(Compra,  Compra.id_cliente  == Cliente.id_cliente)
                .join(Item,    Item.id_compra      == Compra.id_compra)
                .join(Produto, Produto.id_produto  == Item.id_produto)
                .filter(Compra.data_compra >= inicio)
                .group_by(Cliente.id_cliente, Cliente.nome)
                .order_by(func.sum(Produto.preco * Item.quantidade).desc())
                .limit(limite)
                .all()
            )
            return [(r.nome, int(r.qtd_compras), float(r.total_gasto or 0)) for r in rows]
        except SQLAlchemyError:
            self._sessao.rollback()
            return []

    def top_operadores(self, limite: int = 5) -> list[tuple]:
        hoje = datetime.date.today()
        inicio = datetime.datetime(hoje.year, hoje.month, 1)
        try:
            rows = (
                self._sessao.query(
                    Compra.id_operador,
                    func.count(Compra.id_compra).label('qtd_vendas'),
                    func.sum(Produto.preco * Item.quantidade).label('total')
                )
                .join(Item,    Item.id_compra    == Compra.id_compra)
                .join(Produto, Produto.id_produto == Item.id_produto)
                .filter(
                    Compra.data_compra >= inicio,
                    Compra.id_operador.isnot(None),
                )
                .group_by(Compra.id_operador)
                .order_by(func.sum(Produto.preco * Item.quantidade).desc())
                .limit(limite)
                .all()
            )
            return [(r.id_operador, int(r.qtd_vendas), float(r.total or 0)) for r in rows]
        except SQLAlchemyError:
            self._sessao.rollback()
            return []

    def valor_estoque(self) -> float:
        try:
            result = (
                self._sessao.query(func.sum(Produto.preco * Produto.quantidade))
                .scalar()
            )
            return float(result or 0)
        except SQLAlchemyError:
            self._sessao.rollback()
            return 0.0

    def itens_vendidos_por_categoria_mes(self) -> list[tuple]:
        hoje = datetime.date.today()
        inicio = datetime.datetime(hoje.year, hoje.month, 1)
        try:
            rows = (
                self._sessao.query(
                    Produto.nome,
                    func.sum(Item.quantidade).label('qtd_vendida')
                )
                .join(Item,   Item.id_produto  == Produto.id_produto)
                .join(Compra, Compra.id_compra == Item.id_compra)
                .filter(Compra.data_compra >= inicio)
                .group_by(Produto.id_produto, Produto.nome)
                .order_by(func.sum(Item.quantidade).desc())
                .limit(10)
                .all()
            )
            return [(r.nome, int(r.qtd_vendida)) for r in rows]
        except SQLAlchemyError:
            self._sessao.rollback()
            return []

from decimal import Decimal

import pytest

from app.domain.models import ItemCarrinho


def test_subtotal_item_multiplica_quantidade_por_preco():
    item = ItemCarrinho(id_produto=1, nome="Arroz", quantidade=3, preco_unitario=Decimal("5.50"))
    assert item.subtotal == Decimal("16.50")


def test_total_carrinho_soma_subtotais_de_multiplos_itens():
    itens = [
        ItemCarrinho(1, "Arroz", 2, Decimal("5.00")),
        ItemCarrinho(2, "Feijão", 3, Decimal("4.00")),
        ItemCarrinho(3, "Macarrão", 1, Decimal("3.50")),
    ]
    total = sum(i.subtotal for i in itens)
    assert total == Decimal("25.50")


def test_quantidade_zero_levanta_value_error():
    with pytest.raises(ValueError):
        ItemCarrinho(id_produto=1, nome="Arroz", quantidade=0, preco_unitario=Decimal("5.00"))


def test_quantidade_negativa_levanta_value_error():
    with pytest.raises(ValueError):
        ItemCarrinho(id_produto=1, nome="Arroz", quantidade=-1, preco_unitario=Decimal("5.00"))


def test_preco_negativo_levanta_value_error():
    with pytest.raises(ValueError):
        ItemCarrinho(id_produto=1, nome="Arroz", quantidade=1, preco_unitario=Decimal("-0.01"))


def test_carrinho_vazio_retorna_total_zero():
    assert sum(i.subtotal for i in []) == 0

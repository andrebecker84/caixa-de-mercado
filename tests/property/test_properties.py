from decimal import Decimal

from hypothesis import given, settings, strategies as st

from app.domain.models import ItemCarrinho
from app.domain.validators.nome_validator import ValidadorNome

_preco = st.decimals(
    min_value=Decimal("0.01"),
    max_value=Decimal("9999.99"),
    allow_nan=False,
    allow_infinity=False,
    places=2,
)
_quantidade = st.integers(min_value=1, max_value=999)

_validador = ValidadorNome()


@given(quantidade=_quantidade, preco=_preco)
def test_subtotal_nunca_negativo_para_valores_validos(quantidade, preco):
    item = ItemCarrinho(id_produto=1, nome="Produto", quantidade=quantidade, preco_unitario=preco)
    assert item.subtotal >= Decimal("0")


@given(itens_data=st.lists(st.tuples(_quantidade, _preco), min_size=1, max_size=10))
def test_total_carrinho_igual_soma_dos_subtotais(itens_data):
    itens = [
        ItemCarrinho(id_produto=i + 1, nome=f"P{i}", quantidade=qtd, preco_unitario=preco)
        for i, (qtd, preco) in enumerate(itens_data)
    ]
    total_por_soma = sum(i.subtotal for i in itens)
    soma_manual = sum(qtd * preco for qtd, preco in itens_data)
    assert total_por_soma == soma_manual


@given(nome=st.text(max_size=2))
@settings(max_examples=200)
def test_nome_com_menos_de_3_caracteres_e_invalido(nome):
    valido, _ = _validador.validar(nome)
    assert not valido

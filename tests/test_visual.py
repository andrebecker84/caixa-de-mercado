"""
Testes de integração visual com Playwright.

Pré-requisito: flet app rodando em http://localhost:8550
Execute o app antes dos testes:
    python main.py  (ou docker compose up flet)
"""
import pytest


@pytest.mark.skip(reason="Requer servidor Flet ativo em localhost:8550")
def test_titulo_pagina(page):
    page.goto("http://localhost:8550")
    page.wait_for_load_state("networkidle")
    assert "Caixa" in page.title()


@pytest.mark.skip(reason="Requer servidor Flet ativo em localhost:8550")
def test_splash_carrega(page):
    page.goto("http://localhost:8550")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)
    assert page.locator("text=SISTEMA POS").is_visible() or page.locator("canvas").is_visible()

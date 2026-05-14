"""
Testes de integração visual com Playwright.

Pré-requisito: flet app rodando.
  Local:  FLET_URL=http://localhost:8550 pytest tests/test_visual.py
  Docker: docker compose --profile e2e run --rm pw
"""
import os
import pytest

FLET_URL = os.getenv("FLET_URL", "http://localhost:8550")


def test_titulo_pagina(page):
    page.goto(FLET_URL)
    page.wait_for_load_state("networkidle", timeout=20000)
    title = page.title()
    assert title, f"Página sem título: '{title}'"


def test_splash_carrega(page):
    page.goto(FLET_URL)
    page.wait_for_load_state("networkidle", timeout=20000)
    page.wait_for_timeout(4000)
    content = page.content()
    assert len(content) > 500, "Conteúdo Flet não renderizado"

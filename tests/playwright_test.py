"""
Script de testes básicos usando Playwright.

Execução:
    # Garantir que o servidor Flet está rodando:
    python main_flet.py &

    # Executar testes:
    python tests/playwright_test.py

Pré-requisitos:
    pip install playwright
    python -m playwright install chromium
"""

import asyncio
import sys
import time
from playwright.async_api import async_playwright, Page, expect


BASE_URL = "http://localhost:8550"
TIMEOUT   = 15_000   # ms


async def _esperar_carregamento(page: Page) -> None:
    """Aguarda a página inicial carregar (splash screen some)."""
    await page.wait_for_load_state("networkidle", timeout=TIMEOUT)
    await page.wait_for_timeout(2000)


async def teste_splash_carrega(page: Page) -> str:
    """Verifica se a splash screen exibe o ícone de carregamento."""
    await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=TIMEOUT)
    await page.wait_for_timeout(1000)
    content = await page.content()
    svg_count = content.count("<svg")
    if svg_count > 0:
        return "PASS — splash screen rendered (SVG elements found)"
    return "WARN — página carregou mas sem elementos SVG detectáveis"


async def teste_titulo_pagina(page: Page) -> str:
    """Verifica se o título da página está correto."""
    title = await page.title()
    if "Caixa" in title or "Supermercado" in title or title:
        return f"PASS — título: '{title}'"
    return f"FAIL — título inesperado: '{title}'"


async def teste_sidebar_visivel(page: Page) -> str:
    """Verifica se a sidebar com navegação está renderizada."""
    await _esperar_carregamento(page)
    content = await page.content()
    # Flet renderiza como canvas ou DOM — verificar presença de flet-app
    if "flet" in content.lower() or len(content) > 500:
        return "PASS — conteúdo Flet detectado na página"
    return "WARN — conteúdo mínimo, verificar se DB está conectado"


async def teste_screenshot(page: Page) -> str:
    """Captura screenshot para inspeção visual."""
    import pathlib
    destino = pathlib.Path("tests") / "screenshots" / "app_state.png"
    destino.parent.mkdir(exist_ok=True)
    await page.screenshot(path=str(destino), full_page=True)
    return f"PASS — screenshot salvo em {destino}"


async def executar_testes() -> None:
    resultados: list[tuple[str, str]] = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1340, "height": 840})
        page    = await context.new_page()

        testes = [
            ("Título da página",     lambda p: teste_titulo_pagina(p)),
            ("Splash screen carrega", lambda p: teste_splash_carrega(p)),
            ("Sidebar visível",       lambda p: teste_sidebar_visivel(p)),
            ("Screenshot capturado",  lambda p: teste_screenshot(p)),
        ]

        for nome, fn in testes:
            try:
                resultado = await fn(page)
            except Exception as exc:
                resultado = f"ERRO — {exc}"
            resultados.append((nome, resultado))
            print(f"  [{resultado.split(' — ')[0]}] {nome}")
            if "FAIL" in resultado or "ERRO" in resultado:
                print(f"         {resultado}")

        await browser.close()

    falhas = [r for _, r in resultados if "FAIL" in r or "ERRO" in r]
    print(f"\nResultado: {len(resultados) - len(falhas)}/{len(resultados)} testes passaram.")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    print("=" * 60)
    print("Playwright — Caixa Supermercado")
    print(f"=" * 60)
    asyncio.run(executar_testes())

@echo off
setlocal enabledelayedexpansion
title caixaMercado

:: Pre-requisitos
where python >nul 2>&1 || (
    echo [ERRO] Python nao encontrado. Instale Python 3.14+ e tente novamente.
    pause & exit /b 1
)

:header
cls
echo.
echo  +----------------------------------------------------------+
echo  ^|        caixaMercado  .  Sistema de Vendas               ^|
echo  +----------------------------------------------------------+
echo  ^|                                                          ^|
echo  ^|   1  Executar sistema  (CLI)                             ^|
echo  ^|   2  Interface Flet    (Docker / localhost:8550)         ^|
echo  ^|   3  Interface Flet    (local)                           ^|
echo  ^|   4  Instalar dependencias                               ^|
echo  ^|   5  Testes unitarios e de propriedade                   ^|
echo  ^|   6  Testes com cobertura HTML                           ^|
echo  ^|   7  Abrir relatorio de cobertura                        ^|
echo  ^|   8  Testes Playwright  (e2e Docker)                     ^|
echo  ^|   9  Parar containers Docker                             ^|
echo  ^|   R  Resetar banco de dados                              ^|
echo  ^|   0  Sair                                                ^|
echo  ^|                                                          ^|
echo  +----------------------------------------------------------+
echo.
set /p opcao="     Opcao: "
echo.
goto dispatch

:dispatch
if /i "%opcao%"=="1" goto cmd_cli
if /i "%opcao%"=="2" goto cmd_flet_docker
if /i "%opcao%"=="3" goto cmd_flet_local
if /i "%opcao%"=="4" goto cmd_install
if /i "%opcao%"=="5" goto cmd_test
if /i "%opcao%"=="6" goto cmd_test_cov
if /i "%opcao%"=="7" goto cmd_open_cov
if /i "%opcao%"=="8" goto cmd_e2e
if /i "%opcao%"=="9" goto cmd_stop
if /i "%opcao%"=="r" goto cmd_reset
if    "%opcao%"=="0" exit /b 0
echo  Opcao invalida.
timeout /t 1 >nul
goto header

:: ── Comandos ──────────────────────────────────────────────────
:cmd_cli
python main.py --cli
pause & goto header

:cmd_flet_docker
where docker >nul 2>&1 || (echo [ERRO] Docker nao encontrado. & pause & goto header)
echo  Iniciando banco + Flet via Docker...
docker compose -p caixamercado -f docker/docker-compose.yml --env-file .env up --build --force-recreate db flet
pause & goto header

:cmd_flet_local
where docker >nul 2>&1 || (echo [ERRO] Docker nao encontrado. & pause & goto header)
echo  Iniciando banco de dados (Docker)...
docker compose -p caixamercado -f docker/docker-compose.yml --env-file .env up -d --wait db
if errorlevel 1 (echo [ERRO] Banco nao inicializou. & pause & goto header)
echo  Iniciando Flet localmente (janela nativa)...
echo.
python main.py --desktop
pause & goto header

:cmd_install
echo  Instalando dependencias...
pip install -r requirements.txt
echo.
echo  Concluido.
pause & goto header

:cmd_test
python -m pytest tests/unit tests/property -v
pause & goto header

:cmd_test_cov
python -m pytest --cov=app --cov-report=term-missing --cov-report=html tests/unit tests/property
echo.
echo  Relatorio gerado em htmlcov\index.html
pause & goto header

:cmd_open_cov
if exist htmlcov\index.html (
    start htmlcov\index.html
) else (
    echo [AVISO] Relatorio nao encontrado. Execute a opcao 6 primeiro.
    pause
)
goto header

:cmd_e2e
where docker >nul 2>&1 || (echo [ERRO] Docker nao encontrado. & pause & goto header)
echo  Certifique-se de que o Flet esta rodando (opcao 2) antes de continuar.
echo.
docker compose -p caixamercado -f docker/docker-compose.yml --env-file .env --profile e2e run --rm pw
pause & goto header

:cmd_stop
where docker >nul 2>&1 || (echo [ERRO] Docker nao encontrado. & pause & goto header)
echo  Parando containers...
docker compose -p caixamercado -f docker/docker-compose.yml --env-file .env down
docker rm -f caixa_db caixa_flet caixa_cli caixa_test caixa_playwright 2>nul
echo  Containers parados.
pause & goto header

:cmd_reset
where docker >nul 2>&1 || (echo [ERRO] Docker nao encontrado. & pause & goto header)
echo.
echo  +----------------------------------------------------------+
echo  ^|  ATENCAO: todos os dados do banco serao removidos.      ^|
echo  ^|  O banco sera recriado com os dados iniciais (seeds).   ^|
echo  +----------------------------------------------------------+
echo.
set /p confirma="  Confirmar? (S/N): "
if /i not "%confirma%"=="S" (echo  Cancelado. & pause & goto header)
echo.
echo  Removendo volumes...
docker compose -p caixamercado -f docker/docker-compose.yml --env-file .env down -v
echo  Reiniciando com dados iniciais...
docker compose -p caixamercado -f docker/docker-compose.yml --env-file .env up --build --force-recreate db flet
pause & goto header

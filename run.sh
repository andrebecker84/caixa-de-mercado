#!/usr/bin/env bash
set -euo pipefail

# ── Paleta ANSI ──────────────────────────────────────────────
RESET="\033[0m"
BOLD="\033[1m"
DIM="\033[2m"
PRIMARY="\033[38;2;255;77;0m"     # #FF4D00 — cor da marca
SUCCESS="\033[38;2;0;201;167m"    # #00C9A7
DANGER="\033[38;2;255;107;107m"   # #FF6B6B
MUTED="\033[38;2;136;136;136m"    # #888888
WHITE="\033[97m"

# ── Pre-requisitos ────────────────────────────────────────────
_check_python() {
    command -v python3 &>/dev/null || {
        echo -e "${DANGER}[ERRO] Python 3 nao encontrado.${RESET}"
        exit 1
    }
}

_check_docker() {
    command -v docker &>/dev/null || {
        echo -e "${DANGER}[ERRO] Docker nao encontrado. Instale Docker e tente novamente.${RESET}"
        return 1
    }
}

# ── Utilitarios ───────────────────────────────────────────────
_abrir_url() {
    local url="$1"
    if   command -v xdg-open &>/dev/null; then xdg-open "$url" &>/dev/null &
    elif command -v open      &>/dev/null; then open "$url"
    else echo -e "${MUTED}Acesse: ${url}${RESET}"
    fi
}

_abrir_cov() {
    if [ -f htmlcov/index.html ]; then
        _abrir_url "htmlcov/index.html"
    else
        echo -e "${MUTED}Relatorio nao encontrado. Execute a opcao 6 primeiro.${RESET}"
    fi
}

_pause() {
    echo
    read -rp "$(echo -e "${MUTED}Pressione Enter para continuar...${RESET}")"
}

_header() {
    clear
    echo
    echo -e "${PRIMARY}${BOLD}  ╔══════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${PRIMARY}${BOLD}  ║          caixaMercado  ·  Sistema de Vendas              ║${RESET}"
    echo -e "${PRIMARY}${BOLD}  ╠══════════════════════════════════════════════════════════╣${RESET}"
    echo -e "${PRIMARY}${BOLD}  ║${RESET}                                                          ${PRIMARY}${BOLD}║${RESET}"
    echo -e "${PRIMARY}${BOLD}  ║${RESET}   ${WHITE}1${RESET}  Executar sistema  ${MUTED}(CLI)${RESET}                             ${PRIMARY}${BOLD}║${RESET}"
    echo -e "${PRIMARY}${BOLD}  ║${RESET}   ${WHITE}2${RESET}  Interface Flet    ${MUTED}(Docker · localhost:8550)${RESET}         ${PRIMARY}${BOLD}║${RESET}"
    echo -e "${PRIMARY}${BOLD}  ║${RESET}   ${WHITE}3${RESET}  Interface Flet    ${MUTED}(local)${RESET}                           ${PRIMARY}${BOLD}║${RESET}"
    echo -e "${PRIMARY}${BOLD}  ║${RESET}   ${WHITE}4${RESET}  Instalar dependencias                                 ${PRIMARY}${BOLD}║${RESET}"
    echo -e "${PRIMARY}${BOLD}  ║${RESET}   ${WHITE}5${RESET}  Testes unitarios e de propriedade                    ${PRIMARY}${BOLD}║${RESET}"
    echo -e "${PRIMARY}${BOLD}  ║${RESET}   ${WHITE}6${RESET}  Testes com cobertura HTML                             ${PRIMARY}${BOLD}║${RESET}"
    echo -e "${PRIMARY}${BOLD}  ║${RESET}   ${WHITE}7${RESET}  Abrir relatorio de cobertura                          ${PRIMARY}${BOLD}║${RESET}"
    echo -e "${PRIMARY}${BOLD}  ║${RESET}   ${WHITE}8${RESET}  Testes Playwright  ${MUTED}(e2e · Docker)${RESET}                   ${PRIMARY}${BOLD}║${RESET}"
    echo -e "${PRIMARY}${BOLD}  ║${RESET}   ${WHITE}9${RESET}  Parar containers Docker                               ${PRIMARY}${BOLD}║${RESET}"
    echo -e "${PRIMARY}${BOLD}  ║${RESET}   ${DANGER}r${RESET}  Resetar banco de dados                                ${PRIMARY}${BOLD}║${RESET}"
    echo -e "${PRIMARY}${BOLD}  ║${RESET}   ${DANGER}0${RESET}  Sair                                                  ${PRIMARY}${BOLD}║${RESET}"
    echo -e "${PRIMARY}${BOLD}  ║${RESET}                                                          ${PRIMARY}${BOLD}║${RESET}"
    echo -e "${PRIMARY}${BOLD}  ╚══════════════════════════════════════════════════════════╝${RESET}"
    echo
    read -rp "$(echo -e "     ${MUTED}Opcao:${RESET} ")" opcao
    echo
}

# ── Comandos ──────────────────────────────────────────────────
_cmd_cli() {
    python3 main.py --cli
}

_cmd_flet_docker() {
    _check_docker || return
    echo -e "${MUTED}Iniciando banco + Flet via Docker...${RESET}"
    docker compose -p caixamercado -f docker/docker-compose.yml --env-file .env up --build db flet &
    sleep 4
    echo -e "${SUCCESS}Abrindo http://localhost:8550${RESET}"
    _abrir_url "http://localhost:8550"
}

_cmd_flet_local() {
    _check_docker || return
    echo -e "${MUTED}Iniciando banco de dados (Docker)...${RESET}"
    docker compose -p caixamercado -f docker/docker-compose.yml --env-file .env up -d --wait db || {
        echo -e "${DANGER}[ERRO] Banco nao inicializou.${RESET}"
        return
    }
    echo -e "${MUTED}Iniciando Flet localmente (janela nativa)...${RESET}"
    echo
    python3 main.py --desktop
}

_cmd_install() {
    echo -e "${MUTED}Instalando dependencias...${RESET}"
    pip3 install -r requirements.txt
    echo -e "${SUCCESS}Concluido.${RESET}"
}

_cmd_test() {
    python3 -m pytest tests/unit tests/property -v
}

_cmd_test_cov() {
    python3 -m pytest --cov=app --cov-report=term-missing --cov-report=html tests/unit tests/property
    echo -e "\n${SUCCESS}Relatorio gerado em htmlcov/index.html${RESET}"
}

_cmd_e2e() {
    _check_docker || return
    echo -e "${MUTED}Certifique-se de que o Flet esta rodando (opcao 2) antes de continuar.${RESET}"
    echo
    docker compose -p caixamercado -f docker/docker-compose.yml --env-file .env --profile e2e run --rm pw
}

_cmd_stop() {
    _check_docker || return
    echo -e "${MUTED}Parando containers... (dados do banco mantidos)${RESET}"
    docker compose -p caixamercado -f docker/docker-compose.yml --env-file .env down
    echo -e "${SUCCESS}Containers parados.${RESET}"
}

_cmd_reset() {
    _check_docker || return
    echo -e "${DANGER}${BOLD}  ╔══════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${DANGER}${BOLD}  ║  ATENCAO: todos os dados do banco serao removidos.       ║${RESET}"
    echo -e "${DANGER}${BOLD}  ║  O banco sera recriado com os dados iniciais (seeds).    ║${RESET}"
    echo -e "${DANGER}${BOLD}  ╚══════════════════════════════════════════════════════════╝${RESET}"
    echo
    read -rp "$(echo -e "  ${DANGER}Confirmar? (S/N):${RESET} ")" confirma
    if [[ "${confirma^^}" != "S" ]]; then
        echo -e "${MUTED}Cancelado.${RESET}"
        return
    fi
    echo -e "\n${MUTED}Removendo volumes...${RESET}"
    docker compose -p caixamercado -f docker/docker-compose.yml --env-file .env down -v
    echo -e "${MUTED}Reiniciando com dados iniciais...${RESET}"
    docker compose -p caixamercado -f docker/docker-compose.yml --env-file .env up --build db flet
}

# ── Loop principal ────────────────────────────────────────────
_loop() {
    while true; do
        _header
        case "$opcao" in
            1) _cmd_cli          ;;
            2) _cmd_flet_docker  ;;
            3) _cmd_flet_local   ;;
            4) _cmd_install      ;;
            5) _cmd_test         ;;
            6) _cmd_test_cov     ;;
            7) _abrir_cov        ;;
            8) _cmd_e2e          ;;
            9) _cmd_stop         ;;
          r|R) _cmd_reset        ;;
            0) echo -e "${MUTED}Ate logo.${RESET}\n"; exit 0 ;;
            *) echo -e "${MUTED}Opcao invalida.${RESET}" ;;
        esac
        _pause
    done
}

_check_python
_loop

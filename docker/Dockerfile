# syntax=docker/dockerfile:1.10
# ── Base: dependências de produção ─────────────────────────────
FROM python:3.13-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ── CLI interativo ─────────────────────────────────────────────
FROM base AS app

CMD ["python", "main.py", "--cli"]

# ── Frontend Flet (web) ────────────────────────────────────────
FROM base AS flet

EXPOSE 8550

CMD ["python", "main.py"]

# ── Testes unitários + propriedade ────────────────────────────
FROM base AS test

CMD ["pytest", "--cov=app", "--cov-report=term-missing", "--cov-report=html", "tests/unit", "tests/property"]

# ── Playwright e2e ─────────────────────────────────────────────
FROM mcr.microsoft.com/playwright/python:v1.49.0-noble AS playwright

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install chromium

COPY . .

CMD ["pytest", "tests/test_visual.py", "-v", "--tb=short"]

import flet as ft
from app.flet import theme as th
from app.infrastructure.sistema_service import inicializar_banco
import time
import threading


class SplashPage:
    def __init__(self, page: ft.Page, on_ready, on_error=None):
        self._page     = page
        self._on_ready = on_ready
        self._on_error = on_error
        self._alive    = True
        self._status_text = ft.Text(
            "Verificando serviços...", size=14, color=th.muted(self._page)
        )
        self._progress = ft.ProgressBar(
            width=320,
            color=th.primary(self._page),
            bgcolor=ft.Colors.with_opacity(0.1, th.primary(self._page)),
        )

    def show(self):
        self._page.controls.clear()

        logo     = ft.Image(src="/logo.svg", width=120, height=65, fit="contain")
        title    = ft.Text(
            "SISTEMA POS", size=24, weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE, style=ft.TextStyle(letter_spacing=4),
        )
        subtitle = ft.Text(
            "CAIXAMERCADO v2.5", size=10, weight=ft.FontWeight.W_300,
            color=th.muted(self._page), style=ft.TextStyle(letter_spacing=2),
        )

        self._page.add(
            ft.Container(
                content=ft.Column([
                    ft.Column(
                        [logo, title, subtitle],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                    ),
                    ft.Container(height=60),
                    self._progress,
                    ft.Container(height=10),
                    self._status_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                alignment=ft.MainAxisAlignment.CENTER),
                alignment=ft.Alignment(0, 0),
                expand=True,
                bgcolor=th.bg(self._page),
            )
        )
        self._page.update()
        threading.Thread(target=self._health_check_loop, daemon=True).start()

    def _update_status(self, text: str, progress: float | None = None):
        if not self._alive:
            return
        try:
            async def _apply():
                self._status_text.value = text
                if progress is not None:
                    self._progress.value = progress
                self._page.update()
            self._page.run_task(_apply)
        except Exception:
            self._alive = False

    def _run_task_safe(self, coro_fn, *args):
        try:
            self._page.run_task(coro_fn, *args)
        except RuntimeError:
            self._alive = False

    def _health_check_loop(self):
        max_retries    = 20
        retry_interval = 2

        self._update_status("Aguardando inicialização do Banco de Dados...", progress=0.1)

        sessao = None
        for attempt in range(1, max_retries + 1):
            if not self._alive:
                return
            try:
                self._update_status(
                    f"Conectando ao banco (Tentativa {attempt}/{max_retries})...",
                    progress=0.1 + (attempt / max_retries) * 0.4,
                )
                sessao = inicializar_banco()
                if sessao:
                    from sqlalchemy import text
                    sessao.execute(text("SELECT 1"))
                    break
            except Exception:
                time.sleep(retry_interval)

        if not sessao:
            self._update_status("ERRO CRÍTICO: Banco de dados inacessível.", progress=1.0)
            if self._on_error:
                self._run_task_safe(
                    self._on_error,
                    "Falha ao sincronizar com o backend após várias tentativas.",
                )
            return

        self._update_status("Banco 100% OK. Carregando interface...", progress=0.7)
        time.sleep(0.4)
        self._update_status("Tudo pronto!", progress=1.0)
        time.sleep(0.4)

        self._run_task_safe(self._on_ready, sessao)

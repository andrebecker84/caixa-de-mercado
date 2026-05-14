import flet as ft
from app.flet import theme as th


def ui_call(page: ft.Page, fn) -> None:
    """Schedule a sync callable on Flet's event loop from any thread (Flet 0.82+)."""
    async def _():
        fn()
    page.run_task(_)


class PageController:
    def __init__(self, page: ft.Page, body: ft.Column):
        self._page = page
        self._body = body

    @property
    def page(self) -> ft.Page:
        return self._page

    def set_content(self, *controls: ft.Control) -> None:
        self._body.controls = list(controls)
        self._page.update()

    def append_content(self, *controls: ft.Control) -> None:
        self._body.controls.extend(controls)
        self._page.update()

    def clear_content(self) -> None:
        self._body.controls.clear()
        self._page.update()

    def notify(self, message: str, ok: bool = True) -> None:
        color = th.success(self._page) if ok else th.danger(self._page)
        snack = ft.SnackBar(
            content=ft.Text(
                message,
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.W_500,
                no_wrap=False,
            ),
            bgcolor=color,
            duration=3000 if ok else 8000,
            show_close_icon=True,
            close_icon_color=ft.Colors.WHITE,
            open=True,
        )
        self._page.overlay.append(snack)
        self._page.update()

    def show_dialog(self, dialog: ft.AlertDialog) -> None:
        self._page.show_dialog(dialog)

    def close_dialog(self) -> None:
        self._page.pop_dialog()

    def make_card(self, content: ft.Control, padding: int = 24) -> ft.Container:
        return ft.Container(
            content=content,
            bgcolor=th.card(self._page),
            border_radius=ft.border_radius.all(th.RADIUS_CARD),
            shadow=th.card_shadows(th.is_dark(self._page)),
            padding=padding,
        )

    def make_label(self, text: str, size: int = 14, bold: bool = False, color: str | None = None) -> ft.Text:
        return ft.Text(
            text,
            size=size,
            weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL,
            color=color or th.text(self._page),
        )

    def make_muted(self, text: str, size: int = 13) -> ft.Text:
        return ft.Text(text, size=size, color=th.muted(self._page))

    def make_primary_btn(self, label: str, on_click, icon: str | None = None) -> ft.ElevatedButton:
        return ft.ElevatedButton(
            label,
            icon=icon,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor=th.primary(self._page),
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=th.RADIUS_BTN),
                padding=ft.padding.symmetric(horizontal=28, vertical=14),
                animation_duration=180,
            ),
        )

    def make_danger_btn(self, label: str, on_click) -> ft.OutlinedButton:
        return ft.OutlinedButton(
            label,
            on_click=on_click,
            style=ft.ButtonStyle(
                color=th.danger(self._page),
                side=ft.BorderSide(color=th.danger(self._page), width=1.5),
                shape=ft.RoundedRectangleBorder(radius=th.RADIUS_BTN),
                padding=ft.padding.symmetric(horizontal=28, vertical=14),
            ),
        )

    def make_text_field(self, label: str, hint: str = "", keyboard_type=ft.KeyboardType.TEXT) -> ft.TextField:
        return ft.TextField(
            label=label,
            hint_text=hint,
            keyboard_type=keyboard_type,
            border_radius=th.RADIUS_INPUT,
            border_color=th.border(self._page),
            focused_border_color=th.primary(self._page),
            label_style=ft.TextStyle(color=th.muted(self._page)),
            text_style=ft.TextStyle(color=th.text(self._page)),
            bgcolor=th.surface(self._page),
            fill_color=th.surface(self._page),
            filled=True,
            cursor_color=th.primary(self._page),
        )

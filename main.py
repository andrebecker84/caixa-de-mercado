import sys


def main() -> None:
    if "--cli" in sys.argv:
        from app.sistema_controller import iniciar_sistema
        iniciar_sistema()
    else:
        import flet as ft
        from app.flet.app import main as flet_main
        view = ft.AppView.FLET_APP if "--desktop" in sys.argv else ft.AppView.WEB_BROWSER
        ft.run(
            flet_main,
            port=8550,
            view=view,
            assets_dir="assets",
        )


if __name__ == "__main__":
    main()

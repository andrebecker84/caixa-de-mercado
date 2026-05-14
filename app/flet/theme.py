import flet as ft

# Dark palette (Charcoal / Flaming Red theme based on user reference)
DARK_BG      = "#0E0E0E"  # Extremely dark background
DARK_SURFACE = "#1A1A1A"  # Sidebar and navbar surface
DARK_CARD    = "#242424"  # Lighter cards with glass feel
DARK_BORDER  = "#2D2D2D"  # Subtle borders
DARK_PRIMARY = "#FF4B2B"  # Vibrant flaming red-orange
DARK_ACCENT  = "#FF416C"  # Vibrant reddish-pink for gradients
DARK_DANGER  = "#FF3D00"  # Deep red
DARK_WARNING = "#FFCC00"  # Gold/Amber
DARK_SUCCESS = "#00FF99"  # Neon green
DARK_TEXT    = "#FFFFFF"  # Pure white text
DARK_MUTED   = "#888888"  # Soft gray

# Light palette (Still available but modernized)
LIGHT_BG      = "#F8F9FA"
LIGHT_SURFACE = "#FFFFFF"
LIGHT_CARD    = "#FFFFFF"
LIGHT_BORDER  = "#E9ECEF"
LIGHT_PRIMARY = "#FF4B2B"
LIGHT_ACCENT  = "#FF416C"
LIGHT_DANGER  = "#DC3545"
LIGHT_WARNING = "#FFC107"
LIGHT_SUCCESS = "#28A745"
LIGHT_TEXT    = "#212529"
LIGHT_MUTED   = "#6C757D"

RADIUS_CARD  = 28  # Larger, more premium radius
RADIUS_BTN   = 16
RADIUS_INPUT = 14


def card_shadows(dark: bool) -> list:
    opacity = 0.6 if dark else 0.1
    return [
        ft.BoxShadow(
            blur_radius=40,
            color=ft.Colors.with_opacity(opacity, ft.Colors.BLACK),
            offset=ft.Offset(0, 20),
        ),
        ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 4),
        ),
    ]


ANIM_FAST   = ft.Animation(180, ft.AnimationCurve.EASE_OUT)
ANIM_MEDIUM = ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT)


def is_dark(page: ft.Page) -> bool:
    return page.theme_mode != ft.ThemeMode.LIGHT


def bg(page)      -> str: return DARK_BG      if is_dark(page) else LIGHT_BG
def surface(page) -> str: return DARK_SURFACE  if is_dark(page) else LIGHT_SURFACE
def card(page)    -> str: return DARK_CARD     if is_dark(page) else LIGHT_CARD
def border(page)  -> str: return DARK_BORDER   if is_dark(page) else LIGHT_BORDER
def primary(page) -> str: return DARK_PRIMARY  if is_dark(page) else LIGHT_PRIMARY
def accent(page)  -> str: return DARK_ACCENT   if is_dark(page) else LIGHT_ACCENT
def danger(page)  -> str: return DARK_DANGER   if is_dark(page) else LIGHT_DANGER
def success(page) -> str: return DARK_SUCCESS  if is_dark(page) else LIGHT_SUCCESS
def text(page)    -> str: return DARK_TEXT      if is_dark(page) else LIGHT_TEXT
def muted(page)   -> str: return DARK_MUTED    if is_dark(page) else LIGHT_MUTED

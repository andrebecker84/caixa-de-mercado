_PALETTE = [
    "#7C6FCD", "#00C9A7", "#FF6B6B", "#FFB700",
    "#4ECDC4", "#45B7D1", "#A29BFE", "#FD79A8",
]


def avatar_color(entity_id: int) -> str:
    return _PALETTE[entity_id % len(_PALETTE)]


def initials(nome: str) -> str:
    parts = nome.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return nome[:2].upper()

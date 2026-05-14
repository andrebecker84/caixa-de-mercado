import datetime

try:
    from zoneinfo import ZoneInfo as _ZoneInfo
    _TZ = _ZoneInfo('America/Sao_Paulo')
except Exception:
    _TZ = None

_MESES_PT = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]
_DIAS_PT = [
    "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
    "sexta-feira", "sábado", "domingo",
]


def agora() -> datetime.datetime:
    if _TZ:
        return datetime.datetime.now(tz=_TZ)
    return datetime.datetime.now()


def data_longa(dt: datetime.datetime) -> str:
    dia = _DIAS_PT[dt.weekday()].capitalize()
    mes = _MESES_PT[dt.month - 1]
    return f"{dia}, {dt.day:02d} de {mes} de {dt.year}"


def nome_mes(mes: int) -> str:
    return _MESES_PT[mes - 1].capitalize()

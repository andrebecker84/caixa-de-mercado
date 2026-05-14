from app.domain.models import Operador

def buscar_por_id(operadores: list[Operador], id_operador: int) -> Operador | None:
    """Busca um operador pelo seu ID em uma lista."""
    return next((o for o in operadores if o.id_operador == id_operador), None)

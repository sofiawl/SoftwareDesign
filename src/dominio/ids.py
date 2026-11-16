import uuid


def novo_id() -> str:
    """Identificador curto, gerado pela própria entidade ao nascer."""
    return uuid.uuid4().hex[:8]

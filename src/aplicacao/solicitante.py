from dataclasses import dataclass

from dominio.politica.papel import Papel


@dataclass(frozen=True)
class Solicitante:
    """Quem pede a operação. Montado pelo Controller a partir da sessão."""

    id: str
    papel: Papel

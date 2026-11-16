from dataclasses import dataclass
from datetime import datetime

from aplicacao.interfaces.notificador import Aviso


@dataclass(frozen=True)
class AvisoPendente:
    """Aviso que falhou, guardado para nova tentativa (RNF03)."""

    aviso: Aviso
    motivo_falha: str
    criado_em: datetime

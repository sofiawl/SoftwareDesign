from dataclasses import dataclass


@dataclass(frozen=True)
class Resultado:
    """Retorno dos casos de uso que alteram estado."""

    candidatura_id: str | None = None
    vaga_id: str | None = None
    aviso_pendente: bool = False

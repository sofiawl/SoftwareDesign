from dataclasses import dataclass
from enum import Enum

from dominio.erros import DadosInvalidos, RegraViolada


class EstadoCandidatura(Enum):
    ENVIADA = "ENVIADA"
    ACEITA = "ACEITA"
    RECUSADA = "RECUSADA"


@dataclass
class Candidatura:
    id: str
    vaga_id: str
    estudante_id: str
    estado: EstadoCandidatura = EstadoCandidatura.ENVIADA
    motivo_recusa: str | None = None

    def aceitar(self) -> None:
        self._exigir_enviada()
        self.estado = EstadoCandidatura.ACEITA

    def recusar(self, motivo: str) -> None:
        if not motivo or not motivo.strip():
            raise DadosInvalidos("A recusa da candidatura precisa de motivo.")
        self._exigir_enviada()
        self.estado = EstadoCandidatura.RECUSADA
        self.motivo_recusa = motivo.strip()

    def esta_aceita(self) -> bool:
        return self.estado is EstadoCandidatura.ACEITA

    def _exigir_enviada(self) -> None:
        if self.estado is not EstadoCandidatura.ENVIADA:
            raise RegraViolada(f"A candidatura já foi decidida ({self.estado.value}).")

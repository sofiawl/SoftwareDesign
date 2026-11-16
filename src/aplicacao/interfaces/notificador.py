from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class TipoEvento(Enum):
    """Os cinco eventos do RF09."""

    CANDIDATURA_ACEITA = "CANDIDATURA_ACEITA"
    CANDIDATURA_RECUSADA = "CANDIDATURA_RECUSADA"
    ESTAGIO_HOMOLOGADO = "ESTAGIO_HOMOLOGADO"
    DOCUMENTO_RECUSADO = "DOCUMENTO_RECUSADO"
    ESTAGIO_ENCERRADO = "ESTAGIO_ENCERRADO"


@dataclass(frozen=True)
class Aviso:
    destinatario_id: str
    tipo_evento: TipoEvento
    referencia_id: str
    motivo: str | None = None


@dataclass(frozen=True)
class ResultadoAviso:
    sucesso: bool
    motivo_falha: str | None = None

    @staticmethod
    def ok() -> "ResultadoAviso":
        return ResultadoAviso(True)

    @staticmethod
    def falha(motivo: str) -> "ResultadoAviso":
        return ResultadoAviso(False, motivo)


class Notificador(ABC):
    """Contrato: nunca lança exceção, não reenvia e não desfaz nada (ADR-03)."""

    @abstractmethod
    def notificar(self, aviso: Aviso) -> ResultadoAviso: ...

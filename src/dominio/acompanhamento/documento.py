from dataclasses import dataclass
from enum import Enum

from dominio.erros import DadosInvalidos, RegraViolada
from dominio.politica.tipo_documento import TipoDocumento


class EstadoDocumento(Enum):
    PENDENTE = "PENDENTE"
    ENTREGUE = "ENTREGUE"
    RECUSADO = "RECUSADO"


@dataclass
class Documento:
    """Item do processo com tipo e estado, não uma etapa (ADR-02)."""

    tipo: TipoDocumento
    estado: EstadoDocumento = EstadoDocumento.PENDENTE
    motivo_recusa: str | None = None

    def entregar(self) -> None:
        # PENDENTE -> ENTREGUE e RECUSADO -> ENTREGUE (reentrega)
        if self.estado is EstadoDocumento.ENTREGUE:
            raise RegraViolada(f"{self.tipo.nome} já foi entregue.")
        self.estado = EstadoDocumento.ENTREGUE

    def recusar(self, motivo: str) -> None:
        if not motivo or not motivo.strip():
            raise DadosInvalidos("A recusa do documento precisa de motivo.")
        if self.estado is not EstadoDocumento.ENTREGUE:
            raise RegraViolada(f"{self.tipo.nome} não está entregue; só documento entregue pode ser recusado.")
        self.estado = EstadoDocumento.RECUSADO
        self.motivo_recusa = motivo.strip()

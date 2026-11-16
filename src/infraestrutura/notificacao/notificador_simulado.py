import logging

from aplicacao.interfaces.notificador import Aviso, Notificador, ResultadoAviso

_log = logging.getLogger("notificador")


class NotificadorSimulado(Notificador):
    """Canal simulado (RNF04). Guarda os avisos e pode ser configurado para falhar."""

    def __init__(self, falhar: bool = False):
        self.falhar = falhar
        self.emitidos: list[Aviso] = []

    def notificar(self, aviso: Aviso) -> ResultadoAviso:
        if self.falhar:
            _log.warning("FALHA ao avisar %s: %s (%s)", aviso.destinatario_id,
                         aviso.tipo_evento.value, aviso.referencia_id)
            return ResultadoAviso.falha("canal simulado configurado para falhar")
        self.emitidos.append(aviso)
        _log.info("Aviso para %s: %s (%s)%s", aviso.destinatario_id, aviso.tipo_evento.value,
                  aviso.referencia_id, f" motivo: {aviso.motivo}" if aviso.motivo else "")
        return ResultadoAviso.ok()

"""Passo 5 do roteiro comum: avisar depois de gravar (ADR-03, RNF03)."""

from aplicacao.interfaces.notificador import Aviso, Notificador
from aplicacao.interfaces.repositorio_processo import RepositorioProcesso


def avisar(notificador: Notificador, repositorio: RepositorioProcesso, aviso: Aviso) -> bool:
    """Devolve True se o aviso ficou pendente. A decisão já gravada não é desfeita."""
    resultado = notificador.notificar(aviso)
    if resultado.sucesso:
        return False
    repositorio.salvar_aviso_pendente(aviso, resultado.motivo_falha or "falha sem motivo")
    return True

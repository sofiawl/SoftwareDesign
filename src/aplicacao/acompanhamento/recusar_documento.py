from aplicacao import processo
from aplicacao.avisar import avisar
from aplicacao.interfaces.notificador import Aviso, Notificador, TipoEvento
from aplicacao.interfaces.repositorio_processo import RepositorioProcesso
from aplicacao.permissao import exigir_decisao
from aplicacao.resultado import Resultado
from aplicacao.solicitante import Solicitante
from dominio.politica.papel import Etapa
from dominio.politica.politica_estagio import PoliticaEstagio


class RecusarDocumento:
    """RF05 (recusa com motivo) e RF09 (documento recusado)."""

    def __init__(self, repositorio: RepositorioProcesso, politica: PoliticaEstagio,
                 notificador: Notificador):
        self._repositorio = repositorio
        self._politica = politica
        self._notificador = notificador

    def executar(self, solicitante: Solicitante, estagio_id: str, tipo_codigo: str,
                 motivo: str) -> Resultado:
        exigir_decisao(self._politica, Etapa.RECUSA_DOCUMENTO, solicitante)
        estagio = self._repositorio.buscar_estagio(estagio_id)
        estagio.recusar_documento(tipo_codigo, motivo)
        self._repositorio.salvar_estagio(estagio)

        estudante_id = processo.estudante_do_estagio(self._repositorio, estagio)
        pendente = avisar(self._notificador, self._repositorio, Aviso(
            estudante_id, TipoEvento.DOCUMENTO_RECUSADO, estagio.id, motivo.strip()))
        return Resultado(candidatura_id=estagio.candidatura_id, aviso_pendente=pendente)

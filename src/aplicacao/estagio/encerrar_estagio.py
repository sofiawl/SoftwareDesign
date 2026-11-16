from aplicacao import processo
from aplicacao.avisar import avisar
from aplicacao.interfaces.notificador import Aviso, Notificador, TipoEvento
from aplicacao.interfaces.repositorio_processo import RepositorioProcesso
from aplicacao.permissao import exigir_decisao
from aplicacao.resultado import Resultado
from aplicacao.solicitante import Solicitante
from dominio.politica.papel import Etapa
from dominio.politica.politica_estagio import PoliticaEstagio


class EncerrarEstagio:
    """RF08 e RF09 (encerrado)."""

    def __init__(self, repositorio: RepositorioProcesso, politica: PoliticaEstagio,
                 notificador: Notificador):
        self._repositorio = repositorio
        self._politica = politica
        self._notificador = notificador

    def executar(self, solicitante: Solicitante, estagio_id: str, motivo: str) -> Resultado:
        exigir_decisao(self._politica, Etapa.ENCERRAMENTO, solicitante)
        estagio = self._repositorio.buscar_estagio(estagio_id)
        estagio.encerrar(motivo)
        self._repositorio.salvar_estagio(estagio)

        estudante_id = processo.estudante_do_estagio(self._repositorio, estagio)
        pendente = avisar(self._notificador, self._repositorio, Aviso(
            estudante_id, TipoEvento.ESTAGIO_ENCERRADO, estagio.id, estagio.motivo_encerramento))
        return Resultado(candidatura_id=estagio.candidatura_id, aviso_pendente=pendente)

from aplicacao import processo
from aplicacao.avisar import avisar
from aplicacao.interfaces.notificador import Aviso, Notificador, TipoEvento
from aplicacao.interfaces.repositorio_processo import RepositorioProcesso
from aplicacao.permissao import exigir_decisao
from aplicacao.resultado import Resultado
from aplicacao.solicitante import Solicitante
from dominio.erros import RegraViolada
from dominio.estagio.estagio import Estagio
from dominio.politica.papel import Etapa
from dominio.politica.politica_estagio import PoliticaEstagio


class HomologarEstagio:
    """RF04, RF05 (documentos obrigatórios) e RF09 (homologado)."""

    def __init__(self, repositorio: RepositorioProcesso, politica: PoliticaEstagio,
                 notificador: Notificador):
        self._repositorio = repositorio
        self._politica = politica
        self._notificador = notificador

    def executar(self, solicitante: Solicitante, candidatura_id: str,
                 orientador_id: str) -> Resultado:
        exigir_decisao(self._politica, Etapa.HOMOLOGACAO, solicitante)
        candidatura = processo.candidatura(self._repositorio, candidatura_id)
        if self._repositorio.buscar_estagio_da_candidatura(candidatura_id) is not None:
            raise RegraViolada("A candidatura já foi homologada.")

        estagio = Estagio.homologar(candidatura, orientador_id,
                                    self._politica.documentos_obrigatorios())
        self._repositorio.salvar_estagio(estagio)

        pendente = avisar(self._notificador, self._repositorio, Aviso(
            candidatura.estudante_id, TipoEvento.ESTAGIO_HOMOLOGADO, estagio.id))
        return Resultado(candidatura_id=candidatura_id, aviso_pendente=pendente)

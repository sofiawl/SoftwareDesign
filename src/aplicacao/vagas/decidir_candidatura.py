from aplicacao.avisar import avisar
from aplicacao.erros import NaoEncontrado, SemPermissao
from aplicacao.interfaces.notificador import Aviso, Notificador, TipoEvento
from aplicacao.interfaces.repositorio_processo import RepositorioProcesso
from aplicacao.permissao import exigir_decisao
from aplicacao.resultado import Resultado
from aplicacao.solicitante import Solicitante
from dominio.politica.papel import Etapa
from dominio.politica.politica_estagio import PoliticaEstagio


class DecidirCandidatura:
    """RF03 e RF09 (aceita/recusada)."""

    def __init__(self, repositorio: RepositorioProcesso, politica: PoliticaEstagio,
                 notificador: Notificador):
        self._repositorio = repositorio
        self._politica = politica
        self._notificador = notificador

    def executar(self, solicitante: Solicitante, candidatura_id: str,
                 aceitar: bool, motivo: str | None = None) -> Resultado:
        exigir_decisao(self._politica, Etapa.DECISAO_CANDIDATURA, solicitante)
        vaga = self._repositorio.buscar_vaga_da_candidatura(candidatura_id)
        if vaga.concedente_id != solicitante.id:
            raise SemPermissao("A candidatura é de uma vaga de outra concedente.")
        candidatura = vaga.candidatura(candidatura_id)
        if candidatura is None:
            raise NaoEncontrado(f"Candidatura {candidatura_id} não encontrada.")

        if aceitar:
            candidatura.aceitar()
            evento = TipoEvento.CANDIDATURA_ACEITA
        else:
            candidatura.recusar(motivo or "")
            evento = TipoEvento.CANDIDATURA_RECUSADA
        self._repositorio.salvar_vaga(vaga)

        pendente = avisar(self._notificador, self._repositorio, Aviso(
            candidatura.estudante_id, evento, candidatura.id, candidatura.motivo_recusa))
        return Resultado(candidatura_id=candidatura.id, aviso_pendente=pendente)

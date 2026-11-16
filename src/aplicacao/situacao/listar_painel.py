from dataclasses import dataclass

from aplicacao.interfaces.leitura_situacao import LeituraSituacao
from aplicacao.situacao.consultar_situacao import ConsultarSituacao
from aplicacao.solicitante import Solicitante
from dominio.politica.situacao import DadosVaga, SituacaoVisivel


@dataclass(frozen=True)
class Painel:
    vagas: list[DadosVaga]
    processos: list[SituacaoVisivel]


class ListarPainel:
    """Tela inicial: vagas (oferta pública) e os processos que o solicitante pode ver.

    Não tem filtro próprio: cada processo passa por ConsultarSituacao, então o
    RNF01 continua aplicado num ponto só (ASR3).
    """

    def __init__(self, leitura: LeituraSituacao, consultar: ConsultarSituacao):
        self._leitura = leitura
        self._consultar = consultar

    def executar(self, solicitante: Solicitante) -> Painel:
        processos = []
        for candidatura_id in self._leitura.listar_candidaturas():
            visivel = self._consultar.executar(solicitante, candidatura_id)
            if isinstance(visivel, SituacaoVisivel):
                processos.append(visivel)
        return Painel(self._leitura.listar_vagas(), processos)

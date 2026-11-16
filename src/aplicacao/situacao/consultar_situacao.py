from aplicacao.interfaces.leitura_situacao import LeituraSituacao
from aplicacao.solicitante import Solicitante
from dominio.politica.recorte_por_papel import RecortePorPapel
from dominio.politica.situacao import AcessoNegado, SituacaoVisivel


class ConsultarSituacao:
    """RF07 com RNF01 aplicado aqui e em nenhum outro lugar (ASR3)."""

    def __init__(self, leitura: LeituraSituacao, recorte: RecortePorPapel):
        self._leitura = leitura
        self._recorte = recorte

    def executar(self, solicitante: Solicitante, candidatura_id: str) -> SituacaoVisivel | AcessoNegado:
        situacao = self._leitura.carregar(candidatura_id)
        return self._recorte.recortar(situacao, solicitante)

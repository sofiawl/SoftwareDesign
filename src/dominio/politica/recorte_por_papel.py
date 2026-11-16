"""RNF01 aplicado em um ponto só (ASR3)."""

from dominio.politica.papel import Papel
from dominio.politica.situacao import AcessoNegado, SituacaoProcesso, SituacaoVisivel


class RecortePorPapel:
    def recortar(self, situacao: SituacaoProcesso, solicitante) -> SituacaoVisivel | AcessoNegado:
        """`solicitante` é qualquer objeto com `id` e `papel` (o Solicitante da aplicação)."""
        vaga, cand, estagio = situacao.vaga, situacao.candidatura, situacao.estagio
        papel, quem = solicitante.papel, solicitante.id

        completo = (
            papel is Papel.COORDENACAO
            or (papel is Papel.ESTUDANTE and cand.estudante_id == quem)
            or (papel is Papel.CONCEDENTE and vaga.concedente_id == quem)
        )
        if completo:
            return SituacaoVisivel(cand.id, cand.estudante_nome, vaga, cand, estagio)

        if papel is Papel.ORIENTADOR and estagio is not None and estagio.orientador_id == quem:
            # Identidade, documentos e atividades do estágio que orienta;
            # não recebe os dados da candidatura.
            return SituacaoVisivel(cand.id, cand.estudante_nome, vaga, None, estagio)

        return AcessoNegado()

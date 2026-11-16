import unittest

from dominio.politica.papel import Etapa, Papel
from dominio.politica.politica_estagio import PoliticaRegulamentoVigente
from dominio.politica.recorte_por_papel import RecortePorPapel
from dominio.politica.situacao import (
    AcessoNegado, DadosCandidatura, DadosEstagio, DadosVaga, SituacaoProcesso, SituacaoVisivel,
)
from aplicacao.solicitante import Solicitante

VAGA = DadosVaga("v1", "alfa", "Empresa Alfa", "Web", 20, "2027/1", "", "ABERTA")
CAND = DadosCandidatura("c1", "ana", "Ana", "ACEITA", None)
EST = DadosEstagio("e1", "carla", "Carla", "EM_ANDAMENTO", None, (), ())
SIT = SituacaoProcesso(VAGA, CAND, EST)


class TestPolitica(unittest.TestCase):
    def test_quem_decide_cada_etapa(self):  # ASR1
        p = PoliticaRegulamentoVigente()
        self.assertTrue(p.pode_decidir(Etapa.DECISAO_CANDIDATURA, Papel.CONCEDENTE))
        self.assertFalse(p.pode_decidir(Etapa.DECISAO_CANDIDATURA, Papel.COORDENACAO))
        for etapa in (Etapa.HOMOLOGACAO, Etapa.RECUSA_DOCUMENTO, Etapa.ENCERRAMENTO):
            self.assertTrue(p.pode_decidir(etapa, Papel.COORDENACAO))
            self.assertFalse(p.pode_decidir(etapa, Papel.CONCEDENTE))
            self.assertFalse(p.pode_decidir(etapa, Papel.ESTUDANTE))


class TestRecortePorPapel(unittest.TestCase):  # RNF01, ASR3
    def recortar(self, id_, papel, situacao=SIT):
        return RecortePorPapel().recortar(situacao, Solicitante(id_, papel))

    def test_coordenacao_ve_tudo(self):
        r = self.recortar("coord", Papel.COORDENACAO)
        self.assertEqual((r.candidatura, r.estagio), (CAND, EST))

    def test_estudante_ve_o_proprio(self):
        self.assertIsInstance(self.recortar("ana", Papel.ESTUDANTE), SituacaoVisivel)

    def test_outro_estudante_nao_ve(self):
        self.assertIsInstance(self.recortar("bruno", Papel.ESTUDANTE), AcessoNegado)

    def test_concedente_da_vaga_ve_com_nome(self):
        r = self.recortar("alfa", Papel.CONCEDENTE)
        self.assertEqual(r.estudante_nome, "Ana")

    def test_outra_concedente_nao_ve(self):
        self.assertIsInstance(self.recortar("beta", Papel.CONCEDENTE), AcessoNegado)

    def test_orientador_ve_estagio_sem_candidatura(self):
        r = self.recortar("carla", Papel.ORIENTADOR)
        self.assertIsNone(r.candidatura)
        self.assertEqual(r.estagio, EST)

    def test_outro_orientador_nao_ve(self):
        self.assertIsInstance(self.recortar("diego", Papel.ORIENTADOR), AcessoNegado)

    def test_orientador_nao_ve_antes_da_homologacao(self):
        sem_estagio = SituacaoProcesso(VAGA, CAND, None)
        self.assertIsInstance(self.recortar("carla", Papel.ORIENTADOR, sem_estagio), AcessoNegado)

    def test_acesso_negado_nao_carrega_dado(self):
        self.assertEqual(vars(AcessoNegado()), {})

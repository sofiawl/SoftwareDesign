import unittest
from datetime import date

from dominio.acompanhamento.documento import EstadoDocumento
from dominio.erros import DadosInvalidos, RegraViolada
from dominio.estagio.estagio import Estagio, EstadoEstagio
from dominio.politica.tipo_documento import PLANO_ATIVIDADES, RELATORIO, TERMO_COMPROMISSO
from dominio.vagas.candidatura import EstadoCandidatura
from dominio.vagas.vaga import EstadoVaga, Vaga

TIPOS = [TERMO_COMPROMISSO, PLANO_ATIVIDADES, RELATORIO]


def vaga():
    return Vaga.cadastrar("alfa", "Web", 20, "2027/1", "Python")


def estagio_homologado():
    c = vaga().candidatar("ana")
    c.aceitar()
    return Estagio.homologar(c, "carla", TIPOS)


class TestVaga(unittest.TestCase):
    def test_vaga_nasce_aberta(self):  # RF01
        self.assertIs(vaga().estado, EstadoVaga.ABERTA)

    def test_cadastro_rejeita_carga_nao_positiva(self):
        with self.assertRaises(DadosInvalidos):
            Vaga.cadastrar("alfa", "Web", 0, "2027/1", "")

    def test_candidatura_duplicada_e_recusada(self):  # RF02
        v = vaga()
        v.candidatar("ana")
        with self.assertRaises(RegraViolada):
            v.candidatar("ana")

    def test_vaga_encerrada_nao_recebe_candidatura(self):  # RF02
        v = vaga()
        v.encerrar()
        with self.assertRaises(RegraViolada):
            v.candidatar("ana")


class TestCandidatura(unittest.TestCase):
    def test_recusa_exige_motivo(self):  # RF03
        c = vaga().candidatar("ana")
        with self.assertRaises(DadosInvalidos):
            c.recusar("   ")
        self.assertIs(c.estado, EstadoCandidatura.ENVIADA)

    def test_candidatura_decidida_nao_muda(self):
        c = vaga().candidatar("ana")
        c.recusar("perfil diferente")
        with self.assertRaises(RegraViolada):
            c.aceitar()


class TestEstagio(unittest.TestCase):
    def test_homologar_candidatura_nao_aceita_falha(self):  # RF04
        c = vaga().candidatar("ana")
        with self.assertRaises(RegraViolada):
            Estagio.homologar(c, "carla", TIPOS)

    def test_homologacao_cria_documentos_pendentes_da_politica(self):  # RF05, ASR1
        e = estagio_homologado()
        self.assertEqual([d.tipo for d in e.documentos], TIPOS)
        self.assertTrue(all(d.estado is EstadoDocumento.PENDENTE for d in e.documentos))

    def test_documento_recusado_aceita_reentrega(self):  # RF05
        e = estagio_homologado()
        e.entregar_documento("RELATORIO")
        e.recusar_documento("RELATORIO", "falta assinatura")
        e.entregar_documento("RELATORIO")
        self.assertIs(e.documentos[2].estado, EstadoDocumento.ENTREGUE)

    def test_documento_pendente_nao_pode_ser_recusado(self):
        with self.assertRaises(RegraViolada):
            estagio_homologado().recusar_documento("RELATORIO", "x")

    def test_atividade_valida(self):  # RF06
        e = estagio_homologado()
        e.registrar_atividade(date(2027, 3, 1), "Reunião inicial", 4)
        self.assertEqual(len(e.atividades), 1)

    def test_atividade_exige_carga_positiva(self):
        with self.assertRaises(DadosInvalidos):
            estagio_homologado().registrar_atividade(date(2027, 3, 1), "x", 0)

    def test_encerrado_nao_aceita_atividade(self):  # RF08
        e = estagio_homologado()
        e.encerrar("concluído")
        self.assertIs(e.estado, EstadoEstagio.ENCERRADO)
        with self.assertRaises(RegraViolada):
            e.registrar_atividade(date(2027, 3, 1), "x", 1)

    def test_encerramento_exige_motivo(self):  # RF08
        with self.assertRaises(DadosInvalidos):
            estagio_homologado().encerrar("")

"""Casos de uso com repositório em memória e notificador falso: sem banco e sem servidor."""

import unittest
from datetime import date

from aplicacao.acompanhamento.entregar_documento import EntregarDocumento
from aplicacao.acompanhamento.recusar_documento import RecusarDocumento
from aplicacao.acompanhamento.registrar_atividade import RegistrarAtividade
from aplicacao.erros import NaoEncontrado, SemPermissao
from aplicacao.estagio.encerrar_estagio import EncerrarEstagio
from aplicacao.estagio.homologar_estagio import HomologarEstagio
from aplicacao.interfaces.notificador import TipoEvento
from aplicacao.situacao.consultar_situacao import ConsultarSituacao
from aplicacao.situacao.listar_painel import ListarPainel
from aplicacao.solicitante import Solicitante
from aplicacao.vagas.cadastrar_vaga import CadastrarVaga
from aplicacao.vagas.candidatar import Candidatar
from aplicacao.vagas.decidir_candidatura import DecidirCandidatura
from dominio.erros import RegraViolada
from dominio.politica.papel import Papel
from dominio.politica.politica_estagio import PoliticaRegulamentoVigente
from dominio.politica.recorte_por_papel import RecortePorPapel
from dominio.politica.situacao import AcessoNegado
from tests.dubles import NotificadorFalso, RepositorioEmMemoria

ALFA = Solicitante("alfa", Papel.CONCEDENTE)
BETA = Solicitante("beta", Papel.CONCEDENTE)
ANA = Solicitante("ana", Papel.ESTUDANTE)
BRUNO = Solicitante("bruno", Papel.ESTUDANTE)
COORD = Solicitante("coord", Papel.COORDENACAO)
CARLA = Solicitante("carla", Papel.ORIENTADOR)


class Base(unittest.TestCase):
    def setUp(self):
        self.repo = RepositorioEmMemoria()
        self.notif = NotificadorFalso()
        pol = PoliticaRegulamentoVigente()
        self.cadastrar = CadastrarVaga(self.repo)
        self.candidatar = Candidatar(self.repo)
        self.decidir = DecidirCandidatura(self.repo, pol, self.notif)
        self.homologar = HomologarEstagio(self.repo, pol, self.notif)
        self.encerrar = EncerrarEstagio(self.repo, pol, self.notif)
        self.entregar = EntregarDocumento(self.repo)
        self.recusar_doc = RecusarDocumento(self.repo, pol, self.notif)
        self.registrar = RegistrarAtividade(self.repo)
        self.consultar = ConsultarSituacao(self.repo, RecortePorPapel())

    def nova_candidatura(self, estudante=ANA):
        vaga_id = self.cadastrar.executar(ALFA, "Web", 20, "2027/1", "").vaga_id
        return self.candidatar.executar(estudante, vaga_id).candidatura_id

    def novo_estagio(self):
        cid = self.nova_candidatura()
        self.decidir.executar(ALFA, cid, aceitar=True)
        self.homologar.executar(COORD, cid, "carla")
        return cid, self.repo.buscar_estagio_da_candidatura(cid).id


class TestFluxoPrincipal(Base):
    def test_processo_completo(self):
        cid, eid = self.novo_estagio()
        self.entregar.executar(ANA, eid, "TERMO_COMPROMISSO")
        self.registrar.executar(ANA, eid, date(2027, 3, 1), "Onboarding", 4)
        self.encerrar.executar(COORD, eid, "concluído")

        s = self.consultar.executar(ANA, cid)
        self.assertEqual(s.estagio.estado, "ENCERRADO")
        self.assertEqual(s.estagio.documentos[0].estado, "ENTREGUE")
        self.assertEqual(len(s.estagio.atividades), 1)
        self.assertEqual([a.tipo_evento for a in self.notif.avisos],
                         [TipoEvento.CANDIDATURA_ACEITA, TipoEvento.ESTAGIO_HOMOLOGADO,
                          TipoEvento.ESTAGIO_ENCERRADO])
        self.assertTrue(all(a.destinatario_id == "ana" for a in self.notif.avisos))

    def test_recusa_avisa_com_motivo(self):  # RF03, RF09
        cid = self.nova_candidatura()
        self.decidir.executar(ALFA, cid, aceitar=False, motivo="vaga preenchida")
        aviso = self.notif.avisos[0]
        self.assertEqual((aviso.tipo_evento, aviso.motivo),
                         (TipoEvento.CANDIDATURA_RECUSADA, "vaga preenchida"))

    def test_documento_recusado_avisa(self):  # RF05, RF09
        _, eid = self.novo_estagio()
        self.entregar.executar(ANA, eid, "RELATORIO")
        self.recusar_doc.executar(COORD, eid, "RELATORIO", "sem assinatura")
        self.assertEqual(self.notif.avisos[-1].tipo_evento, TipoEvento.DOCUMENTO_RECUSADO)


class TestErros(Base):
    def test_homologar_candidatura_nao_aceita(self):  # fluxo de erro do protótipo
        cid = self.nova_candidatura()
        with self.assertRaises(RegraViolada):
            self.homologar.executar(COORD, cid, "carla")
        self.assertEqual(self.repo.estagios, {})
        self.assertEqual(self.notif.avisos, [])

    def test_homologar_duas_vezes(self):
        cid, _ = self.novo_estagio()
        with self.assertRaises(RegraViolada):
            self.homologar.executar(COORD, cid, "diego")

    def test_concedente_nao_homologa(self):  # política, ASR1
        cid = self.nova_candidatura()
        self.decidir.executar(ALFA, cid, aceitar=True)
        with self.assertRaises(SemPermissao):
            self.homologar.executar(ALFA, cid, "carla")

    def test_concedente_nao_decide_vaga_de_outra(self):
        cid = self.nova_candidatura()
        with self.assertRaises(SemPermissao):
            self.decidir.executar(BETA, cid, aceitar=True)

    def test_estudante_nao_mexe_em_estagio_de_outro(self):
        _, eid = self.novo_estagio()
        with self.assertRaises(SemPermissao):
            self.registrar.executar(BRUNO, eid, date(2027, 3, 1), "x", 1)

    def test_id_inexistente(self):
        with self.assertRaises(NaoEncontrado):
            self.candidatar.executar(ANA, "naoexiste")


class TestAvisoPendente(Base):  # RNF03, ADR-03
    def test_falha_do_aviso_nao_desfaz_a_decisao(self):
        cid = self.nova_candidatura()
        self.notif.falhar = True
        resultado = self.decidir.executar(ALFA, cid, aceitar=True)

        self.assertTrue(resultado.aviso_pendente)
        self.assertTrue(self.repo.buscar_vaga_da_candidatura(cid).candidatura(cid).esta_aceita())
        pendente = self.repo.avisos_pendentes[0]
        self.assertEqual((pendente.aviso.tipo_evento, pendente.aviso.destinatario_id),
                         (TipoEvento.CANDIDATURA_ACEITA, "ana"))
        self.assertTrue(pendente.motivo_falha)

    def test_sucesso_nao_gera_pendente(self):
        cid = self.nova_candidatura()
        self.assertFalse(self.decidir.executar(ALFA, cid, aceitar=True).aviso_pendente)
        self.assertEqual(self.repo.avisos_pendentes, [])


class TestConsulta(Base):  # RF07, RNF01
    def test_outro_estudante_recebe_acesso_negado(self):
        cid = self.nova_candidatura()
        self.assertIsInstance(self.consultar.executar(BRUNO, cid), AcessoNegado)

    def test_orientador_so_depois_da_homologacao(self):
        cid = self.nova_candidatura()
        self.assertIsInstance(self.consultar.executar(CARLA, cid), AcessoNegado)
        self.decidir.executar(ALFA, cid, aceitar=True)
        self.homologar.executar(COORD, cid, "carla")
        self.assertIsNone(self.consultar.executar(CARLA, cid).candidatura)

    def test_painel_mostra_so_o_que_o_recorte_permite(self):
        self.nova_candidatura(ANA)
        self.nova_candidatura(BRUNO)
        painel = ListarPainel(self.repo, self.consultar)
        self.assertEqual([p.estudante_nome for p in painel.executar(ANA).processos], ["Ana"])
        self.assertEqual(len(painel.executar(COORD).processos), 2)
        self.assertEqual(painel.executar(BETA).processos, [])

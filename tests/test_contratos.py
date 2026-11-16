"""Testes de contrato: os mesmos testes rodam contra o dublê e a implementação real (LSP)."""

import os
import tempfile
import unittest
from datetime import date

from aplicacao.erros import NaoEncontrado
from aplicacao.interfaces.notificador import Aviso, ResultadoAviso, TipoEvento
from dominio.estagio.estagio import Estagio
from dominio.politica.tipo_documento import RELATORIO, TERMO_COMPROMISSO
from dominio.vagas.vaga import Vaga
from infraestrutura.identidade.cadastro_usuarios import CadastroUsuarios
from infraestrutura.notificacao.notificador_simulado import NotificadorSimulado
from infraestrutura.persistencia.banco import Banco
from infraestrutura.persistencia.repositorio_persistente import RepositorioPersistente
from tests.dubles import NotificadorFalso, RepositorioEmMemoria


class ContratoRepositorio:
    def novo_repositorio(self):
        raise NotImplementedError

    def setUp(self):
        self.repo = self.novo_repositorio()

    def _vaga_com_candidatura(self):
        vaga = Vaga.cadastrar("alfa", "Web", 20, "2027/1", "Python")
        c = vaga.candidatar("ana")
        c.aceitar()
        self.repo.salvar_vaga(vaga)
        return vaga, c

    def test_salva_e_busca_vaga_com_candidaturas(self):
        vaga, c = self._vaga_com_candidatura()
        lida = self.repo.buscar_vaga(vaga.id)
        self.assertEqual(lida, vaga)
        self.assertEqual(self.repo.buscar_vaga_da_candidatura(c.id).id, vaga.id)

    def test_salva_e_busca_estagio_inteiro(self):
        _, c = self._vaga_com_candidatura()
        e = Estagio.homologar(c, "carla", [TERMO_COMPROMISSO, RELATORIO])
        e.entregar_documento("RELATORIO")
        e.registrar_atividade(date(2027, 3, 1), "Reunião", 2)
        self.repo.salvar_estagio(e)
        self.assertEqual(self.repo.buscar_estagio(e.id), e)
        self.assertEqual(self.repo.buscar_estagio_da_candidatura(c.id), e)

    def test_estagio_inexistente_da_candidatura_e_none(self):
        _, c = self._vaga_com_candidatura()
        self.assertIsNone(self.repo.buscar_estagio_da_candidatura(c.id))

    def test_ids_inexistentes(self):
        for buscar in (self.repo.buscar_vaga, self.repo.buscar_estagio,
                       self.repo.buscar_vaga_da_candidatura, self.repo.carregar):
            with self.assertRaises(NaoEncontrado):
                buscar("naoexiste")

    def test_carregar_junta_as_duas_raizes(self):
        vaga, c = self._vaga_com_candidatura()
        e = Estagio.homologar(c, "carla", [TERMO_COMPROMISSO])
        self.repo.salvar_estagio(e)
        s = self.repo.carregar(c.id)
        self.assertEqual((s.vaga.id, s.candidatura.id, s.estagio.id), (vaga.id, c.id, e.id))
        self.assertEqual(s.candidatura.estado, "ACEITA")
        self.assertEqual(s.estagio.documentos[0].tipo_codigo, "TERMO_COMPROMISSO")

    def test_listagens(self):
        vaga, c = self._vaga_com_candidatura()
        self.assertEqual([v.id for v in self.repo.listar_vagas()], [vaga.id])
        self.assertEqual(self.repo.listar_candidaturas(), [c.id])


class TestContratoEmMemoria(ContratoRepositorio, unittest.TestCase):
    def novo_repositorio(self):
        return RepositorioEmMemoria()


class TestContratoPersistente(ContratoRepositorio, unittest.TestCase):
    def novo_repositorio(self):
        self._dir = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self._dir.name, "teste.db")
        banco = Banco(self.caminho)
        CadastroUsuarios(banco).garantir_usuarios_iniciais()
        return RepositorioPersistente(banco)

    def tearDown(self):
        self._dir.cleanup()

    def test_dados_sobrevivem_ao_reinicio(self):  # RNF02
        vaga, c = self._vaga_com_candidatura()
        e = Estagio.homologar(c, "carla", [RELATORIO])
        self.repo.salvar_estagio(e)
        reiniciado = RepositorioPersistente(Banco(self.caminho))
        self.assertEqual(reiniciado.buscar_vaga(vaga.id), vaga)
        self.assertEqual(reiniciado.buscar_estagio(e.id), e)

    def test_aviso_pendente_gravado(self):  # RNF03
        self.repo.salvar_aviso_pendente(
            Aviso("ana", TipoEvento.ESTAGIO_HOMOLOGADO, "e1"), "canal fora")
        with Banco(self.caminho).conexao() as con:
            linha = con.execute("SELECT * FROM aviso_pendente").fetchone()
        self.assertEqual((linha["tipo_evento"], linha["motivo_falha"]),
                         ("ESTAGIO_HOMOLOGADO", "canal fora"))

    def test_salvar_estagio_e_tudo_ou_nada(self):
        _, c = self._vaga_com_candidatura()
        e = Estagio.homologar(c, "carla", [RELATORIO])
        e.orientador_id = "usuario-inexistente"   # viola a chave estrangeira
        with self.assertRaises(Exception):
            self.repo.salvar_estagio(e)
        self.assertIsNone(self.repo.buscar_estagio_da_candidatura(c.id))
        with Banco(self.caminho).conexao() as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM documento").fetchone()[0], 0)


class ContratoNotificador:
    def novo(self, falhar):
        raise NotImplementedError

    def test_sucesso(self):
        r = self.novo(False).notificar(Aviso("ana", TipoEvento.ESTAGIO_HOMOLOGADO, "e1"))
        self.assertEqual(r, ResultadoAviso.ok())

    def test_falha_devolve_resultado_sem_excecao(self):
        r = self.novo(True).notificar(Aviso("ana", TipoEvento.ESTAGIO_HOMOLOGADO, "e1"))
        self.assertFalse(r.sucesso)
        self.assertTrue(r.motivo_falha)


class TestContratoNotificadorSimulado(ContratoNotificador, unittest.TestCase):
    def novo(self, falhar):
        return NotificadorSimulado(falhar)


class TestContratoNotificadorFalso(ContratoNotificador, unittest.TestCase):
    def novo(self, falhar):
        return NotificadorFalso(falhar)

"""Rotas de ponta a ponta, sem abrir socket: Controller -> caso de uso -> SQLite."""

import os
import tempfile
import unittest

from apresentacao.web import Requisicao
import main


class TestWeb(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.roteador, self.notificador = main.montar(os.path.join(self._dir.name, "web.db"))

    def tearDown(self):
        self._dir.cleanup()

    def _req(self, metodo, caminho, usuario=None, **form):
        cookies = {"usuario": usuario} if usuario else {}
        return self.roteador.despachar(Requisicao(metodo, caminho, form=form, cookies=cookies))

    def _get(self, caminho, usuario=None):
        return self._req("GET", caminho, usuario)

    def _post(self, caminho, usuario=None, **form):
        return self._req("POST", caminho, usuario, **form)

    def _primeira_vaga(self):
        corpo = self._get("/", "ana").corpo
        inicio = corpo.index('action="/vagas/') + len('action="/vagas/')
        return corpo[inicio:corpo.index("/", inicio)]

    def _candidatura(self, estudante="ana"):
        r = self._post(f"/vagas/{self._primeira_vaga()}/candidaturas", estudante)
        self.assertEqual(r.status, 303)
        return r.cabecalhos["Location"].split("/")[2]

    def test_sem_login_redireciona(self):
        self.assertEqual(self._get("/").cabecalhos["Location"], "/login")

    def test_fluxo_feliz(self):
        cid = self._candidatura()
        self.assertEqual(self._post(f"/candidaturas/{cid}/aceite", "alfa").status, 303)
        r = self._post(f"/candidaturas/{cid}/homologacao", "coord", orientador_id="carla")
        self.assertEqual(r.cabecalhos["Location"], f"/candidaturas/{cid}/situacao")
        pagina = self._get(f"/candidaturas/{cid}/situacao", "carla")
        self.assertEqual(pagina.status, 200)
        self.assertIn("Profa. Carla Dias", pagina.corpo)

    def test_candidatura_duplicada_409(self):
        self._candidatura()
        r = self._post(f"/vagas/{self._primeira_vaga()}/candidaturas", "ana")
        self.assertEqual(r.status, 409)

    def test_vaga_encerrada_409(self):
        corpo = self._get("/", "ana").corpo
        trecho = corpo[corpo.index("ENCERRADA"):]
        inicio = trecho.index('action="/vagas/') + len('action="/vagas/')
        vaga_id = trecho[inicio:trecho.index("/", inicio)]
        r = self._post(f"/vagas/{vaga_id}/candidaturas", "ana")
        self.assertEqual(r.status, 409)
        self.assertIn("A vaga está encerrada e não recebe candidaturas.", r.corpo)

    def test_homologar_nao_aceita_409(self):
        cid = self._candidatura()
        r = self._post(f"/candidaturas/{cid}/homologacao", "coord", orientador_id="carla")
        self.assertEqual(r.status, 409)
        self.assertIn("não foi aceita", r.corpo)

    def test_papel_errado_403(self):
        cid = self._candidatura()
        self.assertEqual(self._post(f"/candidaturas/{cid}/aceite", "coord").status, 403)

    def test_recusa_sem_motivo_400(self):
        cid = self._candidatura()
        self.assertEqual(self._post(f"/candidaturas/{cid}/recusa", "alfa", motivo="").status, 400)

    def test_consulta_sem_vinculo_403_sem_dado_pessoal(self):  # RNF01
        cid = self._candidatura("ana")
        r = self._get(f"/candidaturas/{cid}/situacao", "bruno")
        self.assertEqual(r.status, 403)
        self.assertNotIn("Ana Souza", r.corpo)

    def test_inexistente_404(self):
        self.assertEqual(self._get("/candidaturas/xyz/situacao", "coord").status, 404)

    def test_aviso_pendente_aparece_na_tela(self):  # RNF03
        cid = self._candidatura()
        self.notificador.falhar = True
        r = self._post(f"/candidaturas/{cid}/aceite", "alfa")
        self.assertTrue(r.cabecalhos["Location"].endswith("?aviso=pendente"))
        pagina = self.roteador.despachar(Requisicao(
            "GET", f"/candidaturas/{cid}/situacao", query={"aviso": "pendente"},
            cookies={"usuario": "alfa"}))
        self.assertIn("Aviso ao estudante pendente", pagina.corpo)
        self.assertIn("ACEITA", pagina.corpo)

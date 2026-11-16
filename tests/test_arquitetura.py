"""Confere a direção das dependências entre camadas (ADR-01, arquitetura seção 1)."""

import ast
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"


def imports(camada: str):
    for arquivo in (SRC / camada).rglob("*.py"):
        for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8"))):
            if isinstance(no, ast.ImportFrom) and no.module:
                yield arquivo.relative_to(SRC), no.module
            elif isinstance(no, ast.Import):
                for nome in no.names:
                    yield arquivo.relative_to(SRC), nome.name


class TestDependencias(unittest.TestCase):
    def assertNaoImporta(self, camada, proibidas):
        violacoes = [f"{arq} importa {mod}" for arq, mod in imports(camada)
                     if mod.split(".")[0] in proibidas]
        self.assertEqual(violacoes, [])

    def test_dominio_nao_depende_de_nada(self):
        self.assertNaoImporta("dominio", {"aplicacao", "apresentacao", "infraestrutura"})

    def test_aplicacao_so_depende_do_dominio(self):
        self.assertNaoImporta("aplicacao", {"apresentacao", "infraestrutura"})

    def test_apresentacao_nao_conhece_infraestrutura(self):
        self.assertNaoImporta("apresentacao", {"infraestrutura"})

    def test_infraestrutura_nao_conhece_apresentacao(self):
        self.assertNaoImporta("infraestrutura", {"apresentacao"})

    def test_controllers_nao_acessam_repositorio_nem_politica(self):
        proibidos = ("aplicacao.interfaces.repositorio_processo",
                     "aplicacao.interfaces.leitura_situacao",
                     "dominio.politica.politica_estagio")
        violacoes = [f"{arq} importa {mod}" for arq, mod in imports("apresentacao")
                     if mod in proibidos]
        self.assertEqual(violacoes, [])

    def test_casos_de_uso_nao_usam_sql_nem_http(self):
        self.assertNaoImporta("aplicacao", {"sqlite3", "http", "urllib"})

"""Composição: único lugar que conhece as classes concretas de todas as camadas.

Uso:
    python3 src/main.py [--porta 8000] [--banco estagios.db] [--falhar-aviso]
"""

import argparse
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from aplicacao.acompanhamento.entregar_documento import EntregarDocumento
from aplicacao.acompanhamento.recusar_documento import RecusarDocumento
from aplicacao.acompanhamento.registrar_atividade import RegistrarAtividade
from aplicacao.estagio.encerrar_estagio import EncerrarEstagio
from aplicacao.estagio.homologar_estagio import HomologarEstagio
from aplicacao.situacao.consultar_situacao import ConsultarSituacao
from aplicacao.situacao.listar_painel import ListarPainel
from aplicacao.vagas.cadastrar_vaga import CadastrarVaga
from aplicacao.vagas.candidatar import Candidatar
from aplicacao.vagas.decidir_candidatura import DecidirCandidatura
from apresentacao.controllers.acompanhamento_controller import AcompanhamentoController
from apresentacao.controllers.estagio_controller import EstagioController
from apresentacao.controllers.login_controller import LoginController
from apresentacao.controllers.situacao_controller import SituacaoController
from apresentacao.controllers.vaga_controller import VagaController
from apresentacao.sessao import Sessao
from apresentacao.web import Roteador, servir
from dominio.politica.politica_estagio import PoliticaRegulamentoVigente
from dominio.politica.recorte_por_papel import RecortePorPapel
from dominio.vagas.vaga import Vaga
from infraestrutura.identidade.cadastro_usuarios import CadastroUsuarios
from infraestrutura.notificacao.notificador_simulado import NotificadorSimulado
from infraestrutura.persistencia.banco import Banco
from infraestrutura.persistencia.repositorio_persistente import RepositorioPersistente


def montar(caminho_banco: str, falhar_aviso: bool = False):
    """Cria as implementações, injeta nos casos de uso e registra as rotas."""
    banco = Banco(caminho_banco)
    cadastro = CadastroUsuarios(banco)
    cadastro.garantir_usuarios_iniciais()

    repositorio = RepositorioPersistente(banco)   # RepositorioProcesso e LeituraSituacao
    notificador = NotificadorSimulado(falhar=falhar_aviso)
    politica = PoliticaRegulamentoVigente()
    consultar = ConsultarSituacao(repositorio, RecortePorPapel())

    if not repositorio.listar_vagas():
        repositorio.salvar_vaga(Vaga.cadastrar(
            "alfa", "Desenvolvimento web", 20, "2027/1", "Python ou JavaScript"))
        encerrada = Vaga.cadastrar("beta", "Análise de dados", 30, "2027/2", "Estatística")
        encerrada.encerrar()
        repositorio.salvar_vaga(encerrada)

    sessao = Sessao(cadastro.buscar, cadastro.listar)
    login = LoginController(sessao)
    vagas = VagaController(sessao, CadastrarVaga(repositorio), Candidatar(repositorio),
                           DecidirCandidatura(repositorio, politica, notificador))
    estagio = EstagioController(sessao, HomologarEstagio(repositorio, politica, notificador),
                                EncerrarEstagio(repositorio, politica, notificador))
    acompanhamento = AcompanhamentoController(
        sessao, EntregarDocumento(repositorio),
        RecusarDocumento(repositorio, politica, notificador), RegistrarAtividade(repositorio))
    situacao = SituacaoController(sessao, consultar, ListarPainel(repositorio, consultar))

    r = Roteador()
    r.registrar("GET", "/login", login.formulario)
    r.registrar("POST", "/login", login.entrar)
    r.registrar("POST", "/logout", login.sair)
    r.registrar("GET", "/", situacao.painel)
    r.registrar("POST", "/vagas", vagas.cadastrar)
    r.registrar("POST", "/vagas/{vaga_id}/candidaturas", vagas.candidatar)
    r.registrar("POST", "/candidaturas/{id}/aceite", vagas.aceitar)
    r.registrar("POST", "/candidaturas/{id}/recusa", vagas.recusar)
    r.registrar("POST", "/candidaturas/{id}/homologacao", estagio.homologar)
    r.registrar("POST", "/estagios/{id}/encerramento", estagio.encerrar)
    r.registrar("POST", "/estagios/{id}/documentos/{tipo}/entrega", acompanhamento.entregar)
    r.registrar("POST", "/estagios/{id}/documentos/{tipo}/recusa", acompanhamento.recusar)
    r.registrar("POST", "/estagios/{id}/atividades", acompanhamento.registrar_atividade)
    r.registrar("GET", "/candidaturas/{id}/situacao", situacao.consultar)
    return r, notificador


def principal() -> None:
    p = argparse.ArgumentParser(description="Protótipo do gerenciamento de estágios")
    p.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    p.add_argument("--porta", type=int, default=int(os.environ.get("PORTA", "8000")))
    p.add_argument("--banco", default=os.environ.get("BANCO", "estagios.db"))
    p.add_argument("--falhar-aviso", action="store_true",
                   default=os.environ.get("FALHAR_AVISO") == "1",
                   help="o notificador simulado falha, para demonstrar o aviso pendente (RNF03)")
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s: %(message)s")
    roteador, _ = montar(args.banco, args.falhar_aviso)
    servir(roteador, args.host, args.porta)


if __name__ == "__main__":
    principal()

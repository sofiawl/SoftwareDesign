from aplicacao.situacao.consultar_situacao import ConsultarSituacao
from aplicacao.situacao.listar_painel import ListarPainel
from apresentacao.controllers.base import controller
from apresentacao.views import erros as view_erros
from apresentacao.views import painel as view_painel
from apresentacao.views import situacao as view_situacao
from dominio.politica.situacao import AcessoNegado
from apresentacao.web import Resposta

class SituacaoController:
    def __init__(self, sessao, consultar: ConsultarSituacao, listar_painel: ListarPainel):
        self._sessao = sessao
        self._consultar = consultar
        self._listar_painel = listar_painel

    @controller
    def consultar(self, req, solicitante):
        usuario = self._sessao.usuario(req)
        visivel = self._consultar.executar(solicitante, req.params["id"])
        if isinstance(visivel, AcessoNegado):
            return view_erros.erro(403, "Acesso negado",
                                   "Você não tem vínculo com este processo.", None, usuario)
        return Resposta.html(view_situacao.render(
            visivel, usuario, self._sessao.orientadores(),
            aviso_pendente=req.query.get("aviso") == "pendente"))

    @controller
    def painel(self, req, solicitante):
        usuario = self._sessao.usuario(req)
        return Resposta.html(view_painel.render(self._listar_painel.executar(solicitante), usuario))

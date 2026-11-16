from aplicacao.estagio.encerrar_estagio import EncerrarEstagio
from aplicacao.estagio.homologar_estagio import HomologarEstagio
from apresentacao.controllers.base import controller, para_situacao

class EstagioController:
    def __init__(self, sessao, homologar: HomologarEstagio, encerrar: EncerrarEstagio):
        self._sessao = sessao
        self._homologar = homologar
        self._encerrar = encerrar

    @controller
    def homologar(self, req, solicitante):
        return para_situacao(self._homologar.executar(
            solicitante, req.params["id"], req.form.get("orientador_id", "")))

    @controller
    def encerrar(self, req, solicitante):
        return para_situacao(self._encerrar.executar(
            solicitante, req.params["id"], req.form.get("motivo", "")))

from datetime import date

from aplicacao.acompanhamento.entregar_documento import EntregarDocumento
from aplicacao.acompanhamento.recusar_documento import RecusarDocumento
from aplicacao.acompanhamento.registrar_atividade import RegistrarAtividade
from apresentacao.controllers.base import controller, inteiro, para_situacao
from dominio.erros import DadosInvalidos

class AcompanhamentoController:
    def __init__(self, sessao, entregar: EntregarDocumento, recusar: RecusarDocumento,
                 registrar: RegistrarAtividade):
        self._sessao = sessao
        self._entregar = entregar
        self._recusar = recusar
        self._registrar = registrar

    @controller
    def entregar(self, req, solicitante):
        return para_situacao(self._entregar.executar(
            solicitante, req.params["id"], req.params["tipo"]))

    @controller
    def recusar(self, req, solicitante):
        return para_situacao(self._recusar.executar(
            solicitante, req.params["id"], req.params["tipo"], req.form.get("motivo", "")))

    @controller
    def registrar_atividade(self, req, solicitante):
        f = req.form
        try:
            data = date.fromisoformat(f.get("data", ""))
        except ValueError:
            raise DadosInvalidos("Data inválida; use o formato AAAA-MM-DD.")
        return para_situacao(self._registrar.executar(
            solicitante, req.params["id"], data, f.get("descricao", ""),
            inteiro(f.get("carga_horaria"), "Carga horária")))

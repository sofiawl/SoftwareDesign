from aplicacao.vagas.cadastrar_vaga import CadastrarVaga
from aplicacao.vagas.candidatar import Candidatar
from aplicacao.vagas.decidir_candidatura import DecidirCandidatura
from apresentacao.controllers.base import controller, inteiro, para_situacao
from apresentacao.web import Resposta

class VagaController:
    def __init__(self, sessao, cadastrar: CadastrarVaga, candidatar: Candidatar,
                 decidir: DecidirCandidatura):
        self._sessao = sessao
        self._cadastrar = cadastrar
        self._candidatar = candidatar
        self._decidir = decidir

    @controller
    def cadastrar(self, req, solicitante):
        f = req.form
        self._cadastrar.executar(solicitante, f.get("area", ""),
                                 inteiro(f.get("carga_horaria_semanal"), "Carga horária semanal"),
                                 f.get("periodo", ""), f.get("pre_requisitos", ""))
        return Resposta.redirecionar("/")

    @controller
    def candidatar(self, req, solicitante):
        return para_situacao(self._candidatar.executar(solicitante, req.params["vaga_id"]))

    @controller
    def aceitar(self, req, solicitante):
        return para_situacao(self._decidir.executar(solicitante, req.params["id"], aceitar=True))

    @controller
    def recusar(self, req, solicitante):
        return para_situacao(self._decidir.executar(
            solicitante, req.params["id"], aceitar=False, motivo=req.form.get("motivo", "")))

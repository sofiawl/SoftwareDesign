"""Tradução comum de resultado e erro em resposta HTTP (arquitetura, seção 8)."""

from functools import wraps

from aplicacao.erros import NaoEncontrado, SemPermissao
from aplicacao.resultado import Resultado
from apresentacao.views import erros as view_erros
from apresentacao.web import Requisicao, Resposta
from dominio.erros import DadosInvalidos, RegraViolada


def para_situacao(resultado: Resultado) -> Resposta:
    url = f"/candidaturas/{resultado.candidatura_id}/situacao"
    if resultado.aviso_pendente:
        url += "?aviso=pendente"
    return Resposta.redirecionar(url)


def controller(metodo):
    """Exige login, monta o Solicitante e traduz exceções em status HTTP.

    O Controller decorado precisa ter o atributo `_sessao`.
    """

    @wraps(metodo)
    def handler(self, req: Requisicao) -> Resposta:
        usuario = self._sessao.usuario(req)
        solicitante = self._sessao.solicitante(req)
        if solicitante is None:
            return Resposta.redirecionar("/login")
        try:
            return metodo(self, req, solicitante)
        except DadosInvalidos as e:
            return view_erros.erro(400, "Dados inválidos", str(e), req.referer, usuario)
        except SemPermissao as e:
            return view_erros.erro(403, "Sem permissão", str(e), req.referer, usuario)
        except NaoEncontrado as e:
            return view_erros.erro(404, "Não encontrado", str(e), req.referer, usuario)
        except RegraViolada as e:
            return view_erros.erro(409, "Operação não permitida", str(e), req.referer, usuario)
    return handler


def inteiro(valor: str | None, campo: str) -> int:
    try:
        return int(valor or "")
    except ValueError:
        raise DadosInvalidos(f"{campo} deve ser um número inteiro.")

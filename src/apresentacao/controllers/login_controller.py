from apresentacao.sessao import COOKIE
from apresentacao.views import login as view_login
from apresentacao.web import Resposta


class LoginController:
    """Login simples, sem senha: escolhe um usuário cadastrado (protótipo)."""

    def __init__(self, sessao):
        self._sessao = sessao

    def formulario(self, req):
        return Resposta.html(view_login.render(self._sessao.usuarios()))

    def entrar(self, req):
        usuario_id = req.form.get("usuario_id", "")
        if not any(u.id == usuario_id for u in self._sessao.usuarios()):
            return Resposta.html(view_login.render(self._sessao.usuarios(), "Usuário inválido."), 400)
        return Resposta.redirecionar("/", **{"Set-Cookie": f"{COOKIE}={usuario_id}; Path=/; HttpOnly; SameSite=Lax"})

    def sair(self, req):
        return Resposta.redirecionar("/login", **{"Set-Cookie": f"{COOKIE}=; Path=/; Max-Age=0"})

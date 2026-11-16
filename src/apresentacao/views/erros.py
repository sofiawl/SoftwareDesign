from apresentacao.views.layout import e, pagina
from apresentacao.web import Resposta


def erro(status: int, titulo: str, mensagem: str, voltar: str | None, usuario) -> Resposta:
    corpo = (f'<section class="erro"><h1>{e(titulo)}</h1><p>{e(mensagem)}</p>'
             f'<p><a href="{e(voltar or "/")}">Voltar</a></p></section>')
    return Resposta.html(pagina(titulo, corpo, usuario), status)

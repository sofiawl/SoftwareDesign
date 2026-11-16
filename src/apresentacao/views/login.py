from apresentacao.views.layout import e, pagina


def render(usuarios, mensagem: str | None = None) -> str:
    opcoes = "".join(f'<option value="{e(u.id)}">{e(u.nome)} ({e(u.papel)})</option>'
                     for u in usuarios)
    aviso = f'<p class="muted">{e(mensagem)}</p>' if mensagem else ""
    return pagina("Entrar", f"""
<section><h1>Entrar</h1>{aviso}
<p class="muted">Protótipo: login simples, sem senha. Escolha quem você é.</p>
<form class="bloco" method="post" action="/login">
  <select name="usuario_id">{opcoes}</select>
  <button>Entrar</button>
</form></section>""")

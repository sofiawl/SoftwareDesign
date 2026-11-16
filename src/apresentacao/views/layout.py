from html import escape


def e(valor) -> str:
    """Escapa qualquer valor para HTML."""
    return escape("" if valor is None else str(valor))


_CSS = """
:root { --fundo:#f6f7f9; --cartao:#fff; --texto:#1d2330; --suave:#5d6677; --borda:#dde1e8;
        --primaria:#2457c5; --ok:#1d7f4e; --alerta:#a15c00; --erro:#b42318; }
@media (prefers-color-scheme: dark) {
  :root { --fundo:#14171c; --cartao:#1d2128; --texto:#e7e9ee; --suave:#9aa3b2; --borda:#323844;
          --primaria:#7aa2ff; --ok:#4cc38a; --alerta:#f0b44c; --erro:#ff7b72; }
}
* { box-sizing:border-box; }
body { margin:0; font:15px/1.5 system-ui, sans-serif; background:var(--fundo); color:var(--texto); }
header { display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap;
         padding:12px 20px; background:var(--cartao); border-bottom:1px solid var(--borda); }
header a { color:var(--texto); text-decoration:none; font-weight:600; }
main { max-width:960px; margin:0 auto; padding:20px 16px 48px; }
section { background:var(--cartao); border:1px solid var(--borda); border-radius:10px;
          padding:16px 18px; margin-bottom:16px; }
h1 { font-size:1.4rem; margin:0 0 16px; } h2 { font-size:1.1rem; margin:0 0 12px; }
table { width:100%; border-collapse:collapse; } th, td { text-align:left; padding:6px 8px;
        border-bottom:1px solid var(--borda); vertical-align:top; }
th { color:var(--suave); font-weight:500; font-size:.9rem; }
.tabela { overflow-x:auto; }
.estado { display:inline-block; padding:1px 8px; border-radius:99px; font-size:.8rem;
          border:1px solid var(--borda); }
.muted { color:var(--suave); }
form.inline { display:inline-flex; gap:6px; flex-wrap:wrap; align-items:center; margin:2px 0; }
form.bloco { display:grid; gap:8px; max-width:520px; }
input, select, button { font:inherit; padding:5px 9px; border-radius:6px; border:1px solid var(--borda);
                        background:var(--fundo); color:var(--texto); }
button { background:var(--primaria); color:#fff; border:none; cursor:pointer; }
button.secundario { background:transparent; color:var(--primaria); border:1px solid var(--primaria); }
.alerta { border-left:4px solid var(--alerta); } .erro { border-left:4px solid var(--erro); }
dl { display:grid; grid-template-columns:max-content 1fr; gap:4px 16px; margin:0; }
dt { color:var(--suave); }
a { color:var(--primaria); }
"""


def pagina(titulo: str, corpo: str, usuario=None) -> str:
    topo = ""
    if usuario is not None:
        topo = (f'<span>{e(usuario.nome)} <span class="muted">({e(usuario.papel)})</span> '
                f'<form class="inline" method="post" action="/logout">'
                f'<button class="secundario">Sair</button></form></span>')
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)} · Estágios</title><style>{_CSS}</style></head>
<body><header><a href="/">Gerenciamento de estágios</a>{topo}</header>
<main>{corpo}</main></body></html>"""

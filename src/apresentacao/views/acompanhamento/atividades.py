from apresentacao.views.layout import e


def bloco(t, papel) -> str:
    base = f"/estagios/{t.id}"
    linhas = "".join(f"<tr><td>{e(a.data.strftime('%d/%m/%Y'))}</td><td>{e(a.descricao)}</td>"
                     f"<td>{e(a.carga_horaria)} h</td></tr>" for a in t.atividades)
    form = ""
    if papel == "ESTUDANTE":
        form = f"""<h2 style="margin-top:16px">Registrar atividade</h2>
<form class="bloco" method="post" action="{base}/atividades">
  <input name="data" type="date"><input name="descricao" placeholder="Descrição">
  <input name="carga_horaria" type="number" placeholder="Carga horária (h)">
  <button>Registrar</button></form>"""
    return f"""<section><h2>Atividades</h2><div class="tabela"><table>
<tr><th>Data</th><th>Descrição</th><th>Carga horária</th></tr>
{linhas or '<tr><td colspan="3" class="muted">Nenhuma atividade.</td></tr>'}
</table></div>{form}</section>"""

from apresentacao.views.layout import e


def bloco_situacao(v) -> str:
    return f"""<section><h2>Vaga</h2><dl>
<dt>Área</dt><dd>{e(v.area)}</dd><dt>Concedente</dt><dd>{e(v.concedente_nome)}</dd>
<dt>Carga horária</dt><dd>{e(v.carga_horaria_semanal)} h/semana</dd><dt>Período</dt><dd>{e(v.periodo)}</dd>
<dt>Pré-requisitos</dt><dd>{e(v.pre_requisitos) or '—'}</dd><dt>Estado</dt><dd>{e(v.estado)}</dd>
</dl></section>"""


def formulario_cadastro() -> str:
    return """
<section><h2>Cadastrar vaga</h2>
<form class="bloco" method="post" action="/vagas">
  <input name="area" placeholder="Área (ex.: Desenvolvimento web)">
  <input name="carga_horaria_semanal" type="number" placeholder="Carga horária semanal">
  <input name="periodo" placeholder="Período (ex.: 2027/1)">
  <input name="pre_requisitos" placeholder="Pré-requisitos">
  <button>Cadastrar</button>
</form></section>"""


def tabela(vagas, usuario) -> str:
    linhas = []
    for v in vagas:
        acao = ""
        if usuario.papel == "ESTUDANTE":
            acao = (f'<form class="inline" method="post" action="/vagas/{e(v.id)}/candidaturas">'
                    f'<button>Candidatar-se</button></form>')
        linhas.append(f"<tr><td>{e(v.area)}</td><td>{e(v.concedente_nome)}</td>"
                      f"<td>{e(v.carga_horaria_semanal)} h</td><td>{e(v.periodo)}</td>"
                      f"<td>{e(v.pre_requisitos)}</td><td><span class='estado'>{e(v.estado)}</span></td>"
                      f"<td>{acao}</td></tr>")
    return f"""
<section><h2>Vagas</h2><div class="tabela"><table>
<tr><th>Área</th><th>Concedente</th><th>Carga</th><th>Período</th><th>Pré-requisitos</th><th>Estado</th><th></th></tr>
{''.join(linhas) or '<tr><td colspan="7" class="muted">Nenhuma vaga.</td></tr>'}
</table></div></section>"""

from apresentacao.views.layout import e, pagina


def render(painel, usuario) -> str:
    """Exibe o que recebeu. Os processos já vêm recortados por ConsultarSituacao."""
    partes = ["<h1>Painel</h1>"]

    if usuario.papel == "CONCEDENTE":
        partes.append("""
<section><h2>Cadastrar vaga</h2>
<form class="bloco" method="post" action="/vagas">
  <input name="area" placeholder="Área (ex.: Desenvolvimento web)">
  <input name="carga_horaria_semanal" type="number" placeholder="Carga horária semanal">
  <input name="periodo" placeholder="Período (ex.: 2027/1)">
  <input name="pre_requisitos" placeholder="Pré-requisitos">
  <button>Cadastrar</button>
</form></section>""")

    linhas = []
    for v in painel.vagas:
        acao = ""
        if usuario.papel == "ESTUDANTE":
            acao = (f'<form class="inline" method="post" action="/vagas/{e(v.id)}/candidaturas">'
                    f'<button>Candidatar-se</button></form>')
        linhas.append(f"<tr><td>{e(v.area)}</td><td>{e(v.concedente_nome)}</td>"
                      f"<td>{e(v.carga_horaria_semanal)} h</td><td>{e(v.periodo)}</td>"
                      f"<td>{e(v.pre_requisitos)}</td><td><span class='estado'>{e(v.estado)}</span></td>"
                      f"<td>{acao}</td></tr>")
    partes.append(f"""
<section><h2>Vagas</h2><div class="tabela"><table>
<tr><th>Área</th><th>Concedente</th><th>Carga</th><th>Período</th><th>Pré-requisitos</th><th>Estado</th><th></th></tr>
{''.join(linhas) or '<tr><td colspan="7" class="muted">Nenhuma vaga.</td></tr>'}
</table></div></section>""")

    linhas = []
    for p in painel.processos:
        cand = p.candidatura.estado if p.candidatura else "—"
        est = p.estagio.estado if p.estagio else "não homologado"
        linhas.append(f'<tr><td><a href="/candidaturas/{e(p.candidatura_id)}/situacao">'
                      f"{e(p.estudante_nome)}</a></td><td>{e(p.vaga.area)}</td>"
                      f"<td>{e(p.vaga.concedente_nome)}</td><td>{e(cand)}</td><td>{e(est)}</td></tr>")
    partes.append(f"""
<section><h2>Processos que você pode ver</h2><div class="tabela"><table>
<tr><th>Estudante</th><th>Vaga</th><th>Concedente</th><th>Candidatura</th><th>Estágio</th></tr>
{''.join(linhas) or '<tr><td colspan="5" class="muted">Nenhum processo.</td></tr>'}
</table></div></section>""")

    return pagina("Painel", "".join(partes), usuario)

from apresentacao.views.layout import e, pagina
from apresentacao.views.vagas import vaga


def render(painel, usuario) -> str:
    """Exibe o que recebeu. Os processos já vêm recortados por ConsultarSituacao."""
    partes = ["<h1>Painel</h1>"]
    if usuario.papel == "CONCEDENTE":
        partes.append(vaga.formulario_cadastro())
    partes.append(vaga.tabela(painel.vagas, usuario))

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

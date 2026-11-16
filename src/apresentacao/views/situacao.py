"""Tela da situação (RF07). Exibe exatamente a SituacaoVisivel recebida (ASR3).

Os botões de ação aparecem conforme o papel só por conveniência: quem confere a
permissão é o caso de uso, e um POST de quem não pode decidir recebe 403.
"""

from apresentacao.views.layout import e, pagina


def _form(acao: str, rotulo: str, campos: str = "") -> str:
    return (f'<form class="inline" method="post" action="{e(acao)}">{campos}'
            f"<button>{e(rotulo)}</button></form>")


def _motivo(rotulo: str) -> str:
    return f'<input name="motivo" placeholder="{e(rotulo)}">'


def render(s, usuario, orientadores, aviso_pendente: bool = False) -> str:
    papel = usuario.papel
    partes = [f"<h1>Situação do processo de {e(s.estudante_nome)}</h1>"]

    if aviso_pendente:
        partes.append('<section class="alerta"><strong>Aviso ao estudante pendente.</strong> '
                      "A decisão foi registrada, mas o canal de aviso falhou. "
                      "O aviso ficou gravado para nova tentativa (RNF03).</section>")

    v = s.vaga
    partes.append(f"""<section><h2>Vaga</h2><dl>
<dt>Área</dt><dd>{e(v.area)}</dd><dt>Concedente</dt><dd>{e(v.concedente_nome)}</dd>
<dt>Carga horária</dt><dd>{e(v.carga_horaria_semanal)} h/semana</dd><dt>Período</dt><dd>{e(v.periodo)}</dd>
<dt>Pré-requisitos</dt><dd>{e(v.pre_requisitos) or '—'}</dd><dt>Estado</dt><dd>{e(v.estado)}</dd>
</dl></section>""")

    c = s.candidatura
    if c is not None:
        acoes = ""
        base = f"/candidaturas/{c.id}"
        if papel == "CONCEDENTE" and c.estado == "ENVIADA":
            acoes = _form(f"{base}/aceite", "Aceitar") + _form(f"{base}/recusa", "Recusar", _motivo("Motivo da recusa"))
        if papel == "COORDENACAO" and s.estagio is None:
            opcoes = "".join(f'<option value="{e(o.id)}">{e(o.nome)}</option>' for o in orientadores)
            acoes = _form(f"{base}/homologacao", "Homologar",
                          f'<select name="orientador_id">{opcoes}</select>')
        motivo = f"<dt>Motivo da recusa</dt><dd>{e(c.motivo_recusa)}</dd>" if c.motivo_recusa else ""
        partes.append(f"""<section><h2>Candidatura</h2><dl>
<dt>Estudante</dt><dd>{e(c.estudante_nome)}</dd><dt>Estado</dt><dd><span class="estado">{e(c.estado)}</span></dd>{motivo}
</dl><p>{acoes}</p></section>""")

    t = s.estagio
    if t is None:
        partes.append('<section><h2>Estágio</h2><p class="muted">Ainda não homologado.</p></section>')
        return pagina("Situação", "".join(partes), usuario)

    andamento = t.estado == "EM_ANDAMENTO"
    base = f"/estagios/{t.id}"
    encerrar = ""
    if papel == "COORDENACAO" and andamento:
        encerrar = _form(f"{base}/encerramento", "Encerrar estágio", _motivo("Motivo do encerramento"))
    motivo = f"<dt>Motivo do encerramento</dt><dd>{e(t.motivo_encerramento)}</dd>" if t.motivo_encerramento else ""
    partes.append(f"""<section><h2>Estágio</h2><dl>
<dt>Orientador</dt><dd>{e(t.orientador_nome)}</dd><dt>Estado</dt><dd><span class="estado">{e(t.estado)}</span></dd>{motivo}
</dl><p>{encerrar}</p></section>""")

    linhas = []
    for d in t.documentos:
        acao = ""
        if andamento and papel == "ESTUDANTE" and d.estado in ("PENDENTE", "RECUSADO"):
            acao = _form(f"{base}/documentos/{d.tipo_codigo}/entrega",
                         "Reentregar" if d.estado == "RECUSADO" else "Entregar")
        if andamento and papel == "COORDENACAO" and d.estado == "ENTREGUE":
            acao = _form(f"{base}/documentos/{d.tipo_codigo}/recusa", "Recusar", _motivo("Motivo"))
        linhas.append(f"<tr><td>{e(d.tipo_nome)}</td><td><span class='estado'>{e(d.estado)}</span></td>"
                      f"<td>{e(d.motivo_recusa) or ''}</td><td>{acao}</td></tr>")
    partes.append(f"""<section><h2>Documentos</h2><div class="tabela"><table>
<tr><th>Documento</th><th>Estado</th><th>Motivo da recusa</th><th></th></tr>{''.join(linhas)}
</table></div></section>""")

    linhas = "".join(f"<tr><td>{e(a.data.strftime('%d/%m/%Y'))}</td><td>{e(a.descricao)}</td>"
                     f"<td>{e(a.carga_horaria)} h</td></tr>" for a in t.atividades)
    form = ""
    if papel == "ESTUDANTE":
        form = f"""<h2 style="margin-top:16px">Registrar atividade</h2>
<form class="bloco" method="post" action="{base}/atividades">
  <input name="data" type="date"><input name="descricao" placeholder="Descrição">
  <input name="carga_horaria" type="number" placeholder="Carga horária (h)">
  <button>Registrar</button></form>"""
    partes.append(f"""<section><h2>Atividades</h2><div class="tabela"><table>
<tr><th>Data</th><th>Descrição</th><th>Carga horária</th></tr>
{linhas or '<tr><td colspan="3" class="muted">Nenhuma atividade.</td></tr>'}
</table></div>{form}</section>""")

    return pagina("Situação", "".join(partes), usuario)

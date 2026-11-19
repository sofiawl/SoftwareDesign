from apresentacao.views.layout import campo_motivo, e, form_acao


def bloco(t, papel) -> str:
    andamento = t.estado == "EM_ANDAMENTO"
    base = f"/estagios/{t.id}"
    linhas = []
    for d in t.documentos:
        acao = ""
        if andamento and papel == "ESTUDANTE" and d.estado in ("PENDENTE", "RECUSADO"):
            acao = form_acao(f"{base}/documentos/{d.tipo_codigo}/entrega",
                         "Reentregar" if d.estado == "RECUSADO" else "Entregar")
        if andamento and papel == "COORDENACAO" and d.estado == "ENTREGUE":
            acao = form_acao(f"{base}/documentos/{d.tipo_codigo}/recusa", "Recusar", campo_motivo("Motivo"))
        linhas.append(f"<tr><td>{e(d.tipo_nome)}</td><td><span class='estado'>{e(d.estado)}</span></td>"
                      f"<td>{e(d.motivo_recusa) or ''}</td><td>{acao}</td></tr>")
    return f"""<section><h2>Documentos</h2><div class="tabela"><table>
<tr><th>Documento</th><th>Estado</th><th>Motivo da recusa</th><th></th></tr>{''.join(linhas)}
</table></div></section>"""

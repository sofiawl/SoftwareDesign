from apresentacao.views.layout import campo_motivo, e, form_acao


def bloco(s, papel, orientadores) -> str:
    c = s.candidatura
    acoes = ""
    base = f"/candidaturas/{c.id}"
    if papel == "CONCEDENTE" and c.estado == "ENVIADA":
        acoes = form_acao(f"{base}/aceite", "Aceitar") + form_acao(
            f"{base}/recusa", "Recusar", campo_motivo("Motivo da recusa"))
    if papel == "COORDENACAO" and s.estagio is None:
        opcoes = "".join(f'<option value="{e(o.id)}">{e(o.nome)}</option>' for o in orientadores)
        acoes = form_acao(f"{base}/homologacao", "Homologar",
                      f'<select name="orientador_id">{opcoes}</select>')
    motivo = f"<dt>Motivo da recusa</dt><dd>{e(c.motivo_recusa)}</dd>" if c.motivo_recusa else ""
    return f"""<section><h2>Candidatura</h2><dl>
<dt>Estudante</dt><dd>{e(c.estudante_nome)}</dd><dt>Estado</dt><dd><span class="estado">{e(c.estado)}</span></dd>{motivo}
</dl><p>{acoes}</p></section>"""

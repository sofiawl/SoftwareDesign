from apresentacao.views.layout import campo_motivo, e, form_acao


def bloco_ausente() -> str:
    return '<section><h2>Estágio</h2><p class="muted">Ainda não homologado.</p></section>'


def bloco(t, papel) -> str:
    andamento = t.estado == "EM_ANDAMENTO"
    base = f"/estagios/{t.id}"
    encerrar = ""
    if papel == "COORDENACAO" and andamento:
        encerrar = form_acao(f"{base}/encerramento", "Encerrar estágio", campo_motivo("Motivo do encerramento"))
    motivo = f"<dt>Motivo do encerramento</dt><dd>{e(t.motivo_encerramento)}</dd>" if t.motivo_encerramento else ""
    return f"""<section><h2>Estágio</h2><dl>
<dt>Orientador</dt><dd>{e(t.orientador_nome)}</dd><dt>Estado</dt><dd><span class="estado">{e(t.estado)}</span></dd>{motivo}
</dl><p>{encerrar}</p></section>"""

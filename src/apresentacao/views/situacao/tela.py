"""Tela da situação (RF07). Exibe exatamente a SituacaoVisivel recebida (ASR3).

Os botões de ação aparecem conforme o papel só por conveniência: quem confere a
permissão é o caso de uso, e um POST de quem não pode decidir recebe 403.
"""

from apresentacao.views.acompanhamento import atividades, documentos
from apresentacao.views.estagio import estagio
from apresentacao.views.layout import e, pagina
from apresentacao.views.vagas import candidatura, vaga


def render(s, usuario, orientadores, aviso_pendente: bool = False) -> str:
    papel = usuario.papel
    partes = [f"<h1>Situação do processo de {e(s.estudante_nome)}</h1>"]

    if aviso_pendente:
        partes.append('<section class="alerta"><strong>Aviso ao estudante pendente.</strong> '
                      "A decisão foi registrada, mas o canal de aviso falhou. "
                      "O aviso ficou gravado para nova tentativa (RNF03).</section>")

    partes.append(vaga.bloco_situacao(s.vaga))
    if s.candidatura is not None:
        partes.append(candidatura.bloco(s, papel, orientadores))
    if s.estagio is None:
        partes.append(estagio.bloco_ausente())
        return pagina("Situação", "".join(partes), usuario)

    partes.append(estagio.bloco(s.estagio, papel))
    partes.append(documentos.bloco(s.estagio, papel))
    partes.append(atividades.bloco(s.estagio, papel))
    return pagina("Situação", "".join(partes), usuario)

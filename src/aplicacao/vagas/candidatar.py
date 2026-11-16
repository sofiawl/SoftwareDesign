from aplicacao.interfaces.repositorio_processo import RepositorioProcesso
from aplicacao.permissao import exigir_papel
from aplicacao.resultado import Resultado
from aplicacao.solicitante import Solicitante
from dominio.politica.papel import Papel


class Candidatar:
    """RF02."""

    def __init__(self, repositorio: RepositorioProcesso):
        self._repositorio = repositorio

    def executar(self, solicitante: Solicitante, vaga_id: str) -> Resultado:
        exigir_papel(solicitante, Papel.ESTUDANTE)
        vaga = self._repositorio.buscar_vaga(vaga_id)
        candidatura = vaga.candidatar(solicitante.id)
        self._repositorio.salvar_vaga(vaga)
        return Resultado(candidatura_id=candidatura.id, vaga_id=vaga.id)

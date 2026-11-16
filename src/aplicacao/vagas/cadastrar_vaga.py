from aplicacao.interfaces.repositorio_processo import RepositorioProcesso
from aplicacao.permissao import exigir_papel
from aplicacao.resultado import Resultado
from aplicacao.solicitante import Solicitante
from dominio.politica.papel import Papel
from dominio.vagas.vaga import Vaga


class CadastrarVaga:
    """RF01."""

    def __init__(self, repositorio: RepositorioProcesso):
        self._repositorio = repositorio

    def executar(self, solicitante: Solicitante, area: str, carga_horaria_semanal: int,
                 periodo: str, pre_requisitos: str) -> Resultado:
        exigir_papel(solicitante, Papel.CONCEDENTE)
        vaga = Vaga.cadastrar(solicitante.id, area, carga_horaria_semanal, periodo, pre_requisitos)
        self._repositorio.salvar_vaga(vaga)
        return Resultado(vaga_id=vaga.id)

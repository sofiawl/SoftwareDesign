from datetime import date

from aplicacao import processo
from aplicacao.interfaces.repositorio_processo import RepositorioProcesso
from aplicacao.permissao import exigir_papel
from aplicacao.resultado import Resultado
from aplicacao.solicitante import Solicitante
from dominio.politica.papel import Papel


class RegistrarAtividade:
    """RF06."""

    def __init__(self, repositorio: RepositorioProcesso):
        self._repositorio = repositorio

    def executar(self, solicitante: Solicitante, estagio_id: str, data: date,
                 descricao: str, carga_horaria: int) -> Resultado:
        exigir_papel(solicitante, Papel.ESTUDANTE)
        estagio = self._repositorio.buscar_estagio(estagio_id)
        processo.exigir_dono_do_estagio(self._repositorio, estagio, solicitante)
        estagio.registrar_atividade(data, descricao, carga_horaria)
        self._repositorio.salvar_estagio(estagio)
        return Resultado(candidatura_id=estagio.candidatura_id)

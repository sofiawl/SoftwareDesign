from dataclasses import dataclass
from datetime import date

from dominio.erros import DadosInvalidos
from dominio.ids import novo_id


@dataclass(frozen=True)
class Atividade:
    """Não conhece o estado do estágio: essa regra é do Estagio."""

    id: str
    data: date
    descricao: str
    carga_horaria: int

    @staticmethod
    def nova(data: date, descricao: str, carga_horaria: int) -> "Atividade":
        if not descricao or not descricao.strip():
            raise DadosInvalidos("A atividade precisa de descrição.")
        if carga_horaria <= 0:
            raise DadosInvalidos("A carga horária da atividade deve ser positiva.")
        return Atividade(novo_id(), data, descricao.strip(), carga_horaria)

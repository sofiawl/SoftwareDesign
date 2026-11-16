from dataclasses import dataclass, field
from enum import Enum

from dominio.erros import DadosInvalidos, RegraViolada
from dominio.ids import novo_id
from dominio.vagas.candidatura import Candidatura


class EstadoVaga(Enum):
    ABERTA = "ABERTA"
    ENCERRADA = "ENCERRADA"


@dataclass
class Vaga:
    """Raiz de agregado: contém as candidaturas."""

    id: str
    concedente_id: str
    area: str
    carga_horaria_semanal: int
    periodo: str
    pre_requisitos: str
    estado: EstadoVaga = EstadoVaga.ABERTA
    candidaturas: list[Candidatura] = field(default_factory=list)

    @staticmethod
    def cadastrar(concedente_id: str, area: str, carga_horaria_semanal: int,
                  periodo: str, pre_requisitos: str) -> "Vaga":
        if not area or not area.strip():
            raise DadosInvalidos("A vaga precisa de área.")
        if not periodo or not periodo.strip():
            raise DadosInvalidos("A vaga precisa de período.")
        if carga_horaria_semanal <= 0:
            raise DadosInvalidos("A carga horária semanal deve ser positiva.")
        return Vaga(novo_id(), concedente_id, area.strip(), carga_horaria_semanal,
                    periodo.strip(), (pre_requisitos or "").strip())

    def candidatar(self, estudante_id: str) -> Candidatura:
        if self.estado is not EstadoVaga.ABERTA:
            raise RegraViolada("A vaga está encerrada e não recebe candidaturas.")
        if any(c.estudante_id == estudante_id for c in self.candidaturas):
            raise RegraViolada("O estudante já se candidatou a esta vaga.")
        candidatura = Candidatura(novo_id(), self.id, estudante_id)
        self.candidaturas.append(candidatura)
        return candidatura

    def candidatura(self, candidatura_id: str) -> Candidatura | None:
        return next((c for c in self.candidaturas if c.id == candidatura_id), None)

    def encerrar(self) -> None:
        self.estado = EstadoVaga.ENCERRADA

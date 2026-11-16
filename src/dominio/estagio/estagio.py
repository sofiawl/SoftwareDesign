from dataclasses import dataclass, field
from datetime import date
from enum import Enum

from dominio.acompanhamento.atividade import Atividade
from dominio.acompanhamento.documento import Documento
from dominio.erros import DadosInvalidos, RegraViolada
from dominio.ids import novo_id
from dominio.politica.tipo_documento import TipoDocumento
from dominio.vagas.candidatura import Candidatura


class EstadoEstagio(Enum):
    EM_ANDAMENTO = "EM_ANDAMENTO"
    ENCERRADO = "ENCERRADO"


@dataclass
class Estagio:
    """Raiz de agregado: contém documentos e atividades."""

    id: str
    candidatura_id: str
    orientador_id: str
    estado: EstadoEstagio = EstadoEstagio.EM_ANDAMENTO
    motivo_encerramento: str | None = None
    documentos: list[Documento] = field(default_factory=list)
    atividades: list[Atividade] = field(default_factory=list)

    @staticmethod
    def homologar(candidatura: Candidatura, orientador_id: str,
                  tipos_obrigatorios: list[TipoDocumento]) -> "Estagio":
        """Fábrica: Estágio -> Vagas, nunca o contrário (GRASP Creator)."""
        if not candidatura.esta_aceita():
            raise RegraViolada("Candidatura que não foi aceita não pode ser homologada.")
        if not orientador_id:
            raise DadosInvalidos("A homologação precisa de um orientador.")
        return Estagio(
            novo_id(), candidatura.id, orientador_id,
            documentos=[Documento(t) for t in tipos_obrigatorios],
        )

    def entregar_documento(self, tipo_codigo: str) -> None:
        self._exigir_em_andamento()
        self._documento(tipo_codigo).entregar()

    def recusar_documento(self, tipo_codigo: str, motivo: str) -> None:
        self._exigir_em_andamento()
        self._documento(tipo_codigo).recusar(motivo)

    def registrar_atividade(self, data: date, descricao: str, carga_horaria: int) -> Atividade:
        self._exigir_em_andamento()
        atividade = Atividade.nova(data, descricao, carga_horaria)
        self.atividades.append(atividade)
        return atividade

    def encerrar(self, motivo: str) -> None:
        if not motivo or not motivo.strip():
            raise DadosInvalidos("O encerramento precisa de motivo.")
        self._exigir_em_andamento()
        self.estado = EstadoEstagio.ENCERRADO
        self.motivo_encerramento = motivo.strip()

    def _documento(self, tipo_codigo: str) -> Documento:
        for doc in self.documentos:
            if doc.tipo.codigo == tipo_codigo:
                return doc
        raise RegraViolada(f"O documento {tipo_codigo} não é exigido neste estágio.")

    def _exigir_em_andamento(self) -> None:
        if self.estado is not EstadoEstagio.EM_ANDAMENTO:
            raise RegraViolada("O estágio está encerrado.")

from abc import ABC, abstractmethod

from aplicacao.interfaces.notificador import Aviso
from dominio.estagio.estagio import Estagio
from dominio.vagas.vaga import Vaga


class RepositorioProcesso(ABC):
    """Registro único do processo (ADR-02). Lança NaoEncontrado para id inexistente."""

    @abstractmethod
    def buscar_vaga(self, vaga_id: str) -> Vaga: ...

    @abstractmethod
    def buscar_vaga_da_candidatura(self, candidatura_id: str) -> Vaga: ...

    @abstractmethod
    def salvar_vaga(self, vaga: Vaga) -> None:
        """Grava a vaga e todas as candidaturas, ou nada."""

    @abstractmethod
    def buscar_estagio(self, estagio_id: str) -> Estagio: ...

    @abstractmethod
    def buscar_estagio_da_candidatura(self, candidatura_id: str) -> Estagio | None:
        """Estágio criado a partir da candidatura, ou None se ainda não homologada."""

    @abstractmethod
    def salvar_estagio(self, estagio: Estagio) -> None:
        """Grava o estágio, documentos e atividades, ou nada."""

    @abstractmethod
    def salvar_aviso_pendente(self, aviso: Aviso, motivo_falha: str) -> None: ...

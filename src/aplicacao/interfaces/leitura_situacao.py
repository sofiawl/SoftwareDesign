from abc import ABC, abstractmethod

from dominio.politica.situacao import DadosVaga, SituacaoProcesso


class LeituraSituacao(ABC):
    """Leitura das duas raízes juntas. Não aplica filtro de papel (ASR3)."""

    @abstractmethod
    def carregar(self, candidatura_id: str) -> SituacaoProcesso:
        """Lança NaoEncontrado se a candidatura não existir."""

    @abstractmethod
    def listar_vagas(self) -> list[DadosVaga]:
        """Todas as vagas. Oferta pública, sem dado pessoal de estudante."""

    @abstractmethod
    def listar_candidaturas(self) -> list[str]:
        """Ids de todas as candidaturas; o recorte decide quais o solicitante vê."""

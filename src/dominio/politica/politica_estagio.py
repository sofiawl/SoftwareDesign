"""Lugar único das regras do regulamento (ASR1)."""

from abc import ABC, abstractmethod

from dominio.politica.papel import Etapa, Papel
from dominio.politica.tipo_documento import (
    PLANO_ATIVIDADES,
    RELATORIO,
    TERMO_COMPROMISSO,
    TipoDocumento,
)


class PoliticaEstagio(ABC):
    @abstractmethod
    def documentos_obrigatorios(self) -> list[TipoDocumento]:
        """Tipos de documento exigidos hoje."""

    @abstractmethod
    def pode_decidir(self, etapa: Etapa, papel: Papel) -> bool:
        """Se o papel aprova a etapa."""


class PoliticaRegulamentoVigente(PoliticaEstagio):
    _DOCUMENTOS = (TERMO_COMPROMISSO, PLANO_ATIVIDADES, RELATORIO)

    _APROVADORES = {
        Etapa.DECISAO_CANDIDATURA: {Papel.CONCEDENTE},
        Etapa.HOMOLOGACAO: {Papel.COORDENACAO},
        Etapa.RECUSA_DOCUMENTO: {Papel.COORDENACAO},
        Etapa.ENCERRAMENTO: {Papel.COORDENACAO},
    }

    def documentos_obrigatorios(self) -> list[TipoDocumento]:
        return list(self._DOCUMENTOS)

    def pode_decidir(self, etapa: Etapa, papel: Papel) -> bool:
        return papel in self._APROVADORES.get(etapa, set())

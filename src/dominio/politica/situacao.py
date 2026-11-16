"""Modelos de leitura da consulta de situação (RF07).

SituacaoProcesso é produzida só por LeituraSituacao e consumida só por
RecortePorPapel. SituacaoVisivel é o que chega ao Controller e à View.
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DadosVaga:
    id: str
    concedente_id: str
    concedente_nome: str
    area: str
    carga_horaria_semanal: int
    periodo: str
    pre_requisitos: str
    estado: str


@dataclass(frozen=True)
class DadosCandidatura:
    id: str
    estudante_id: str
    estudante_nome: str
    estado: str
    motivo_recusa: str | None


@dataclass(frozen=True)
class DadosDocumento:
    tipo_codigo: str
    tipo_nome: str
    estado: str
    motivo_recusa: str | None


@dataclass(frozen=True)
class DadosAtividade:
    data: date
    descricao: str
    carga_horaria: int


@dataclass(frozen=True)
class DadosEstagio:
    id: str
    orientador_id: str
    orientador_nome: str
    estado: str
    motivo_encerramento: str | None
    documentos: tuple[DadosDocumento, ...]
    atividades: tuple[DadosAtividade, ...]


@dataclass(frozen=True)
class SituacaoProcesso:
    """Situação completa, sem filtro de papel."""

    vaga: DadosVaga
    candidatura: DadosCandidatura
    estagio: DadosEstagio | None


@dataclass(frozen=True)
class SituacaoVisivel:
    """O que o solicitante pode ver. Campo None = não visível ou inexistente."""

    candidatura_id: str
    estudante_nome: str
    vaga: DadosVaga
    candidatura: DadosCandidatura | None
    estagio: DadosEstagio | None


@dataclass(frozen=True)
class AcessoNegado:
    """Resultado do recorte sem vínculo. Não carrega nenhum dado pessoal."""

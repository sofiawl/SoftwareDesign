from enum import Enum


class Papel(Enum):
    """Os quatro atores do RNF01."""

    CONCEDENTE = "CONCEDENTE"
    ESTUDANTE = "ESTUDANTE"
    COORDENACAO = "COORDENACAO"
    ORIENTADOR = "ORIENTADOR"


class Etapa(Enum):
    """Etapas em que a política diz quem decide (ASR1)."""

    DECISAO_CANDIDATURA = "DECISAO_CANDIDATURA"
    HOMOLOGACAO = "HOMOLOGACAO"
    RECUSA_DOCUMENTO = "RECUSA_DOCUMENTO"
    ENCERRAMENTO = "ENCERRAMENTO"

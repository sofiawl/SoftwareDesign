from dataclasses import dataclass


@dataclass(frozen=True)
class TipoDocumento:
    """Tipo de documento do estágio. É um valor, não um enum fixo (ASR1)."""

    codigo: str
    nome: str


TERMO_COMPROMISSO = TipoDocumento("TERMO_COMPROMISSO", "Termo de compromisso")
PLANO_ATIVIDADES = TipoDocumento("PLANO_ATIVIDADES", "Plano de atividades")
RELATORIO = TipoDocumento("RELATORIO", "Relatório")

# Todos os tipos que já existiram no regulamento, para reconstruir documentos
# gravados mesmo depois que um tipo deixa de ser obrigatório.
_CATALOGO = {t.codigo: t for t in (TERMO_COMPROMISSO, PLANO_ATIVIDADES, RELATORIO)}


def tipo_por_codigo(codigo: str) -> TipoDocumento:
    return _CATALOGO.get(codigo, TipoDocumento(codigo, codigo))

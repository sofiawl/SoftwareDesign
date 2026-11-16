"""Erros de regra do domínio. A apresentação traduz cada um num status HTTP."""


class ErroDominio(Exception):
    """Base dos erros levantados pelas entidades."""


class DadosInvalidos(ErroDominio):
    """Entrada que nunca é válida: motivo vazio, carga horária não positiva..."""


class RegraViolada(ErroDominio):
    """Operação válida em si, mas proibida no estado atual do processo."""

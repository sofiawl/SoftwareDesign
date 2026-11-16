class SemPermissao(Exception):
    """O papel do solicitante não pode executar a operação."""


class NaoEncontrado(Exception):
    """Contrato do repositório: id inexistente."""

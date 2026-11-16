"""Checagens de permissão comuns aos casos de uso."""

from aplicacao.erros import SemPermissao
from aplicacao.solicitante import Solicitante
from dominio.politica.papel import Etapa, Papel
from dominio.politica.politica_estagio import PoliticaEstagio


def exigir_decisao(politica: PoliticaEstagio, etapa: Etapa, solicitante: Solicitante) -> None:
    if not politica.pode_decidir(etapa, solicitante.papel):
        raise SemPermissao(f"O papel {solicitante.papel.value} não decide a etapa {etapa.value}.")


def exigir_papel(solicitante: Solicitante, papel: Papel) -> None:
    if solicitante.papel is not papel:
        raise SemPermissao(f"Operação exclusiva do papel {papel.value}.")

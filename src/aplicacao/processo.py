"""Leituras auxiliares sobre as raízes, usadas por mais de um caso de uso."""

from aplicacao.erros import NaoEncontrado, SemPermissao
from aplicacao.interfaces.repositorio_processo import RepositorioProcesso
from aplicacao.solicitante import Solicitante
from dominio.estagio.estagio import Estagio
from dominio.vagas.candidatura import Candidatura


def candidatura(repositorio: RepositorioProcesso, candidatura_id: str) -> Candidatura:
    vaga = repositorio.buscar_vaga_da_candidatura(candidatura_id)
    c = vaga.candidatura(candidatura_id)
    if c is None:
        raise NaoEncontrado(f"Candidatura {candidatura_id} não encontrada.")
    return c


def estudante_do_estagio(repositorio: RepositorioProcesso, estagio: Estagio) -> str:
    return candidatura(repositorio, estagio.candidatura_id).estudante_id


def exigir_dono_do_estagio(repositorio: RepositorioProcesso, estagio: Estagio,
                           solicitante: Solicitante) -> None:
    if estudante_do_estagio(repositorio, estagio) != solicitante.id:
        raise SemPermissao("O estágio não é do estudante solicitante.")

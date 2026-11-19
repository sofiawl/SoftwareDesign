"""Dublês da aplicação: repositório em memória e notificador que conta e falha sob comando."""

import copy
from datetime import datetime

from aplicacao.erros import NaoEncontrado
from aplicacao.interfaces.aviso_pendente import AvisoPendente
from aplicacao.interfaces.leitura_situacao import LeituraSituacao
from aplicacao.interfaces.notificador import Aviso, Notificador, ResultadoAviso
from aplicacao.interfaces.repositorio_processo import RepositorioProcesso
from dominio.politica.situacao import (
    DadosAtividade, DadosCandidatura, DadosDocumento, DadosEstagio, DadosVaga, SituacaoProcesso,
)

NOMES = {"alfa": "Empresa Alfa", "beta": "Empresa Beta", "ana": "Ana", "bruno": "Bruno",
         "coord": "Coordenação", "carla": "Carla", "diego": "Diego"}


class RepositorioEmMemoria(RepositorioProcesso, LeituraSituacao):
    def __init__(self):
        self.vagas = {}
        self.estagios = {}
        self.avisos_pendentes: list[AvisoPendente] = []

    # cópias, para que alterar a entidade sem salvar não mude o "banco"
    def buscar_vaga(self, vaga_id):
        if vaga_id not in self.vagas:
            raise NaoEncontrado(vaga_id)
        return copy.deepcopy(self.vagas[vaga_id])

    def buscar_vaga_da_candidatura(self, candidatura_id):
        for v in self.vagas.values():
            if v.candidatura(candidatura_id):
                return copy.deepcopy(v)
        raise NaoEncontrado(candidatura_id)

    def salvar_vaga(self, vaga):
        self.vagas[vaga.id] = copy.deepcopy(vaga)

    def buscar_estagio(self, estagio_id):
        if estagio_id not in self.estagios:
            raise NaoEncontrado(estagio_id)
        return copy.deepcopy(self.estagios[estagio_id])

    def buscar_estagio_da_candidatura(self, candidatura_id):
        for e in self.estagios.values():
            if e.candidatura_id == candidatura_id:
                return copy.deepcopy(e)
        return None

    def salvar_estagio(self, estagio):
        self.estagios[estagio.id] = copy.deepcopy(estagio)

    def salvar_aviso_pendente(self, aviso, motivo_falha):
        self.avisos_pendentes.append(AvisoPendente(aviso, motivo_falha, datetime.now()))

    def carregar(self, candidatura_id):
        vaga = self.buscar_vaga_da_candidatura(candidatura_id)
        c = vaga.candidatura(candidatura_id)
        e = self.buscar_estagio_da_candidatura(candidatura_id)
        estagio = None if e is None else DadosEstagio(
            e.id, e.orientador_id, NOMES.get(e.orientador_id, e.orientador_id), e.estado.value,
            e.motivo_encerramento,
            tuple(DadosDocumento(d.tipo.codigo, d.tipo.nome, d.estado.value, d.motivo_recusa)
                  for d in e.documentos),
            tuple(DadosAtividade(a.data, a.descricao, a.carga_horaria) for a in e.atividades))
        return SituacaoProcesso(
            self._dados_vaga(vaga),
            DadosCandidatura(c.id, c.estudante_id, NOMES.get(c.estudante_id, c.estudante_id),
                             c.estado.value, c.motivo_recusa),
            estagio)

    def listar_vagas(self):
        return [self._dados_vaga(v) for v in self.vagas.values()]

    def listar_candidaturas(self):
        return [c.id for v in self.vagas.values() for c in v.candidaturas]

    @staticmethod
    def _dados_vaga(v):
        return DadosVaga(v.id, v.concedente_id, NOMES.get(v.concedente_id, v.concedente_id), v.area,
                         v.carga_horaria_semanal, v.periodo, v.pre_requisitos, v.estado.value)


class NotificadorFalso(Notificador):
    def __init__(self, falhar=False):
        self.falhar = falhar
        self.avisos: list[Aviso] = []

    def notificar(self, aviso):
        if self.falhar:
            return ResultadoAviso.falha("falha simulada no teste")
        self.avisos.append(aviso)
        return ResultadoAviso.ok()

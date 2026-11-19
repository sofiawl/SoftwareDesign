"""Implementa RepositorioProcesso e LeituraSituacao sobre o mesmo banco (ADR-02)."""

from datetime import date, datetime

from aplicacao.erros import NaoEncontrado
from aplicacao.interfaces.aviso_pendente import AvisoPendente
from aplicacao.interfaces.leitura_situacao import LeituraSituacao
from aplicacao.interfaces.notificador import Aviso
from aplicacao.interfaces.repositorio_processo import RepositorioProcesso
from dominio.acompanhamento.atividade import Atividade
from dominio.acompanhamento.documento import Documento, EstadoDocumento
from dominio.estagio.estagio import Estagio, EstadoEstagio
from dominio.politica.situacao import (
    DadosAtividade,
    DadosCandidatura,
    DadosDocumento,
    DadosEstagio,
    DadosVaga,
    SituacaoProcesso,
)
from dominio.politica.tipo_documento import tipo_por_codigo
from dominio.vagas.candidatura import Candidatura, EstadoCandidatura
from dominio.vagas.vaga import EstadoVaga, Vaga
from infraestrutura.persistencia.banco import Banco


class RepositorioPersistente(RepositorioProcesso, LeituraSituacao):
    def __init__(self, banco: Banco):
        self._banco = banco

    # ---------- RepositorioProcesso: vagas ----------

    def buscar_vaga(self, vaga_id: str) -> Vaga:
        with self._banco.conexao() as con:
            linha = con.execute("SELECT * FROM vaga WHERE id = ?", (vaga_id,)).fetchone()
            if linha is None:
                raise NaoEncontrado(f"Vaga {vaga_id} não encontrada.")
            cands = con.execute(
                "SELECT * FROM candidatura WHERE vaga_id = ? ORDER BY rowid", (vaga_id,)).fetchall()
        return Vaga(
            linha["id"], linha["concedente_id"], linha["area"], linha["carga_horaria_semanal"],
            linha["periodo"], linha["pre_requisitos"], EstadoVaga(linha["estado"]),
            [Candidatura(c["id"], c["vaga_id"], c["estudante_id"],
                         EstadoCandidatura(c["estado"]), c["motivo_recusa"]) for c in cands],
        )

    def buscar_vaga_da_candidatura(self, candidatura_id: str) -> Vaga:
        with self._banco.conexao() as con:
            linha = con.execute(
                "SELECT vaga_id FROM candidatura WHERE id = ?", (candidatura_id,)).fetchone()
        if linha is None:
            raise NaoEncontrado(f"Candidatura {candidatura_id} não encontrada.")
        return self.buscar_vaga(linha["vaga_id"])

    def salvar_vaga(self, vaga: Vaga) -> None:
        with self._banco.conexao() as con:
            con.execute(
                """INSERT INTO vaga (id, concedente_id, area, carga_horaria_semanal, periodo,
                                     pre_requisitos, estado)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(id) DO UPDATE SET area = excluded.area,
                       carga_horaria_semanal = excluded.carga_horaria_semanal,
                       periodo = excluded.periodo, pre_requisitos = excluded.pre_requisitos,
                       estado = excluded.estado""",
                (vaga.id, vaga.concedente_id, vaga.area, vaga.carga_horaria_semanal,
                 vaga.periodo, vaga.pre_requisitos, vaga.estado.value))
            for c in vaga.candidaturas:
                con.execute(
                    """INSERT INTO candidatura (id, vaga_id, estudante_id, estado, motivo_recusa)
                       VALUES (?, ?, ?, ?, ?)
                       ON CONFLICT(id) DO UPDATE SET estado = excluded.estado,
                           motivo_recusa = excluded.motivo_recusa""",
                    (c.id, vaga.id, c.estudante_id, c.estado.value, c.motivo_recusa))

    # ---------- RepositorioProcesso: estágio ----------

    def buscar_estagio(self, estagio_id: str) -> Estagio:
        with self._banco.conexao() as con:
            linha = con.execute("SELECT * FROM estagio WHERE id = ?", (estagio_id,)).fetchone()
            if linha is None:
                raise NaoEncontrado(f"Estágio {estagio_id} não encontrado.")
            return self._montar_estagio(con, linha)

    def buscar_estagio_da_candidatura(self, candidatura_id: str) -> Estagio | None:
        with self._banco.conexao() as con:
            linha = con.execute(
                "SELECT * FROM estagio WHERE candidatura_id = ?", (candidatura_id,)).fetchone()
            return None if linha is None else self._montar_estagio(con, linha)

    def salvar_estagio(self, estagio: Estagio) -> None:
        with self._banco.conexao() as con:
            con.execute(
                """INSERT INTO estagio (id, candidatura_id, orientador_id, estado, motivo_encerramento)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT(id) DO UPDATE SET orientador_id = excluded.orientador_id,
                       estado = excluded.estado, motivo_encerramento = excluded.motivo_encerramento""",
                (estagio.id, estagio.candidatura_id, estagio.orientador_id,
                 estagio.estado.value, estagio.motivo_encerramento))
            for d in estagio.documentos:
                con.execute(
                    """INSERT INTO documento (estagio_id, tipo, estado, motivo_recusa)
                       VALUES (?, ?, ?, ?)
                       ON CONFLICT(estagio_id, tipo) DO UPDATE SET estado = excluded.estado,
                           motivo_recusa = excluded.motivo_recusa""",
                    (estagio.id, d.tipo.codigo, d.estado.value, d.motivo_recusa))
            for a in estagio.atividades:
                con.execute(
                    """INSERT OR IGNORE INTO atividade (id, estagio_id, data, descricao, carga_horaria)
                       VALUES (?, ?, ?, ?, ?)""",
                    (a.id, estagio.id, a.data.isoformat(), a.descricao, a.carga_horaria))

    def salvar_aviso_pendente(self, aviso: Aviso, motivo_falha: str) -> None:
        pendente = AvisoPendente(aviso, motivo_falha, datetime.now())
        with self._banco.conexao() as con:
            con.execute(
                """INSERT INTO aviso_pendente (tipo_evento, referencia_id, destinatario_id, motivo,
                                               motivo_falha, criado_em)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (pendente.aviso.tipo_evento.value, pendente.aviso.referencia_id,
                 pendente.aviso.destinatario_id, pendente.aviso.motivo, pendente.motivo_falha,
                 pendente.criado_em.isoformat(timespec="seconds")))

    def _montar_estagio(self, con, linha) -> Estagio:
        docs = con.execute(
            "SELECT * FROM documento WHERE estagio_id = ? ORDER BY rowid", (linha["id"],)).fetchall()
        ativs = con.execute(
            "SELECT * FROM atividade WHERE estagio_id = ? ORDER BY data, rowid", (linha["id"],)).fetchall()
        return Estagio(
            linha["id"], linha["candidatura_id"], linha["orientador_id"],
            EstadoEstagio(linha["estado"]), linha["motivo_encerramento"],
            [Documento(tipo_por_codigo(d["tipo"]), EstadoDocumento(d["estado"]), d["motivo_recusa"])
             for d in docs],
            [Atividade(a["id"], date.fromisoformat(a["data"]), a["descricao"], a["carga_horaria"])
             for a in ativs],
        )

    # ---------- LeituraSituacao ----------

    def carregar(self, candidatura_id: str) -> SituacaoProcesso:
        """Uma leitura só, juntando as duas raízes e os nomes (ASR3)."""
        with self._banco.conexao() as con:
            c = con.execute(
                """SELECT c.*, u.nome AS estudante_nome FROM candidatura c
                   JOIN usuario u ON u.id = c.estudante_id WHERE c.id = ?""",
                (candidatura_id,)).fetchone()
            if c is None:
                raise NaoEncontrado(f"Candidatura {candidatura_id} não encontrada.")
            v = con.execute(self._SQL_VAGA + " WHERE v.id = ?", (c["vaga_id"],)).fetchone()
            e = con.execute(
                """SELECT e.*, u.nome AS orientador_nome FROM estagio e
                   JOIN usuario u ON u.id = e.orientador_id WHERE e.candidatura_id = ?""",
                (candidatura_id,)).fetchone()
            estagio = None
            if e is not None:
                docs = con.execute(
                    "SELECT * FROM documento WHERE estagio_id = ? ORDER BY rowid", (e["id"],)).fetchall()
                ativs = con.execute(
                    "SELECT * FROM atividade WHERE estagio_id = ? ORDER BY data, rowid",
                    (e["id"],)).fetchall()
                estagio = DadosEstagio(
                    e["id"], e["orientador_id"], e["orientador_nome"], e["estado"],
                    e["motivo_encerramento"],
                    tuple(DadosDocumento(d["tipo"], tipo_por_codigo(d["tipo"]).nome, d["estado"],
                                         d["motivo_recusa"]) for d in docs),
                    tuple(DadosAtividade(date.fromisoformat(a["data"]), a["descricao"],
                                         a["carga_horaria"]) for a in ativs),
                )
        return SituacaoProcesso(
            self._dados_vaga(v),
            DadosCandidatura(c["id"], c["estudante_id"], c["estudante_nome"], c["estado"],
                             c["motivo_recusa"]),
            estagio,
        )

    def listar_vagas(self) -> list[DadosVaga]:
        with self._banco.conexao() as con:
            linhas = con.execute(self._SQL_VAGA + " ORDER BY v.rowid").fetchall()
        return [self._dados_vaga(v) for v in linhas]

    def listar_candidaturas(self) -> list[str]:
        with self._banco.conexao() as con:
            return [l["id"] for l in con.execute("SELECT id FROM candidatura ORDER BY rowid")]

    _SQL_VAGA = """SELECT v.*, u.nome AS concedente_nome FROM vaga v
                   JOIN usuario u ON u.id = v.concedente_id"""

    @staticmethod
    def _dados_vaga(v) -> DadosVaga:
        return DadosVaga(v["id"], v["concedente_id"], v["concedente_nome"], v["area"],
                         v["carga_horaria_semanal"], v["periodo"], v["pre_requisitos"], v["estado"])

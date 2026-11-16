"""Login simples sobre a tabela usuario, sem senha real (arquitetura, seção 6).

Substituível por autenticação institucional (SSO); afeta só a apresentação.
"""

from dataclasses import dataclass

from infraestrutura.persistencia.banco import Banco

USUARIOS_INICIAIS = [
    ("alfa", "Empresa Alfa", "rh@alfa.example", "CONCEDENTE"),
    ("beta", "Empresa Beta", "rh@beta.example", "CONCEDENTE"),
    ("ana", "Ana Souza", "ana@aluno.example", "ESTUDANTE"),
    ("bruno", "Bruno Lima", "bruno@aluno.example", "ESTUDANTE"),
    ("coord", "Coordenação de Estágios", "coord@inst.example", "COORDENACAO"),
    ("carla", "Profa. Carla Dias", "carla@inst.example", "ORIENTADOR"),
    ("diego", "Prof. Diego Reis", "diego@inst.example", "ORIENTADOR"),
]


@dataclass(frozen=True)
class Usuario:
    id: str
    nome: str
    papel: str


class CadastroUsuarios:
    def __init__(self, banco: Banco):
        self._banco = banco

    def garantir_usuarios_iniciais(self) -> None:
        with self._banco.conexao() as con:
            con.executemany(
                "INSERT OR IGNORE INTO usuario (id, nome, email, papel) VALUES (?, ?, ?, ?)",
                USUARIOS_INICIAIS)

    def listar(self) -> list[Usuario]:
        with self._banco.conexao() as con:
            return [Usuario(l["id"], l["nome"], l["papel"])
                    for l in con.execute("SELECT id, nome, papel FROM usuario ORDER BY rowid")]

    def buscar(self, usuario_id: str) -> Usuario | None:
        with self._banco.conexao() as con:
            l = con.execute("SELECT id, nome, papel FROM usuario WHERE id = ?",
                            (usuario_id,)).fetchone()
        return None if l is None else Usuario(l["id"], l["nome"], l["papel"])

import sqlite3
from contextlib import contextmanager
from pathlib import Path

_ESQUEMA = (Path(__file__).parent / "esquema.sql").read_text(encoding="utf-8")


class Banco:
    """Arquivo SQLite. Uma conexão por operação, para servir várias threads."""

    def __init__(self, caminho: str):
        self._caminho = caminho
        with self.conexao() as con:
            con.executescript(_ESQUEMA)

    @contextmanager
    def conexao(self):
        """Transação: confirma tudo ao sair sem erro, desfaz tudo se houver erro."""
        con = sqlite3.connect(self._caminho)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        try:
            with con:
                yield con
        finally:
            con.close()

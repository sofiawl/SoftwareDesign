"""Identifica o solicitante a partir do cookie. É a única parte da apresentação
que muda ao trocar o login simples por autenticação institucional."""

from typing import Callable

from aplicacao.solicitante import Solicitante
from apresentacao.web import Requisicao
from dominio.politica.papel import Papel

COOKIE = "usuario"


class Sessao:
    def __init__(self, buscar_usuario: Callable, listar_usuarios: Callable):
        """`buscar_usuario(id)` e `listar_usuarios()` devolvem objetos com id, nome e papel."""
        self._buscar = buscar_usuario
        self._listar = listar_usuarios

    def usuario(self, req: Requisicao):
        usuario_id = req.cookies.get(COOKIE)
        return self._buscar(usuario_id) if usuario_id else None

    def solicitante(self, req: Requisicao) -> Solicitante | None:
        u = self.usuario(req)
        return None if u is None else Solicitante(u.id, Papel(u.papel))

    def usuarios(self):
        return self._listar()

    def orientadores(self):
        return [u for u in self._listar() if u.papel == Papel.ORIENTADOR.value]

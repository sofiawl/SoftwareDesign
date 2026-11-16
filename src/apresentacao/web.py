"""HTTP mínimo sobre a biblioteca padrão: requisição, resposta, rotas e servidor."""

import logging
import re
from dataclasses import dataclass, field
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable
from urllib.parse import parse_qs, urlsplit

_log = logging.getLogger("web")


@dataclass
class Requisicao:
    metodo: str
    caminho: str
    query: dict[str, str] = field(default_factory=dict)
    form: dict[str, str] = field(default_factory=dict)
    cookies: dict[str, str] = field(default_factory=dict)
    referer: str | None = None
    params: dict[str, str] = field(default_factory=dict)


@dataclass
class Resposta:
    status: int = 200
    corpo: str = ""
    cabecalhos: dict[str, str] = field(default_factory=dict)

    @staticmethod
    def html(corpo: str, status: int = 200) -> "Resposta":
        return Resposta(status, corpo, {"Content-Type": "text/html; charset=utf-8"})

    @staticmethod
    def redirecionar(url: str, **cabecalhos: str) -> "Resposta":
        return Resposta(303, "", {"Location": url, **cabecalhos})


Handler = Callable[[Requisicao], Resposta]


class Roteador:
    def __init__(self):
        self._rotas: list[tuple[str, re.Pattern, Handler]] = []
        self.nao_encontrado: Handler = lambda req: Resposta.html("Não encontrado", 404)

    def registrar(self, metodo: str, padrao: str, handler: Handler) -> None:
        regex = re.sub(r"\{(\w+)\}", r"(?P<\1>[^/]+)", padrao)
        self._rotas.append((metodo, re.compile(f"^{regex}$"), handler))

    def despachar(self, req: Requisicao) -> Resposta:
        for metodo, regex, handler in self._rotas:
            m = regex.match(req.caminho)
            if m and metodo == req.metodo:
                req.params = m.groupdict()
                return handler(req)
        return self.nao_encontrado(req)


def _primeiros(qs: str) -> dict[str, str]:
    return {k: v[0] for k, v in parse_qs(qs, keep_blank_values=True).items()}


def servir(roteador: Roteador, host: str, porta: int) -> None:
    class _Handler(BaseHTTPRequestHandler):
        def _tratar(self, metodo: str) -> None:
            url = urlsplit(self.path)
            form = {}
            if metodo == "POST":
                tamanho = int(self.headers.get("Content-Length") or 0)
                form = _primeiros(self.rfile.read(tamanho).decode("utf-8"))
            cookies = {k: m.value for k, m in SimpleCookie(self.headers.get("Cookie", "")).items()}
            req = Requisicao(metodo, url.path, _primeiros(url.query), form, cookies,
                             self.headers.get("Referer"))
            resp = roteador.despachar(req)
            corpo = resp.corpo.encode("utf-8")
            self.send_response(resp.status)
            for nome, valor in resp.cabecalhos.items():
                self.send_header(nome, valor)
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        def do_GET(self):
            self._tratar("GET")

        def do_POST(self):
            self._tratar("POST")

        def log_message(self, formato, *args):
            _log.info(formato, *args)

    servidor = ThreadingHTTPServer((host, porta), _Handler)
    _log.info("Servindo em http://%s:%d", host, porta)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()

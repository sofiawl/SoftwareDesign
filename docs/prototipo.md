# Protótipo

Implementação da [proposta arquitetural](arquitetura.md) em Python, só com a biblioteca padrão: `http.server` (apresentação), `sqlite3` (persistência) e `unittest` (testes). As pastas de `src/` seguem a seção "Organização do código" da arquitetura; os nomes de métodos estão em `snake_case` (`podeDecidir` → `pode_decidir`).

## O que o protótipo demonstra

| Item exigido | Onde |
|---|---|
| Caso de uso que modifica o estado | `HomologarEstagio` (e os outros oito) |
| Consulta | `ConsultarSituacao`, em `GET /candidaturas/{id}/situacao`, com o recorte do RNF01 |
| Fluxo alternativo ou erro | homologar candidatura não aceita (`409`), candidatura duplicada (`409`), papel sem permissão (`403`), recusa sem motivo (`400`), consulta sem vínculo (`403`) |
| Persistência | `RepositorioPersistente` sobre SQLite (`estagios.db`); os dados sobrevivem ao reinício (RNF02) |
| Dependência externa substituível | `Notificador`, implementado por `NotificadorSimulado`; com `--falhar-aviso` a decisão fica e o aviso é gravado em `aviso_pendente` (RNF03) |

## Roteiro de demonstração

1. `python3 src/main.py` e abrir <http://127.0.0.1:8000>.
2. Entrar como **Ana Souza** (estudante) e clicar em *Candidatar-se*. Clicar de novo mostra o erro de candidatura duplicada.
3. Entrar como **Coordenação** e abrir o processo: *Homologar* agora dá `409`, porque a candidatura não foi aceita.
4. Entrar como **Empresa Alfa** e aceitar a candidatura. O terminal mostra o aviso simulado.
5. Entrar como **Coordenação** e homologar com **Profa. Carla Dias**. Os três documentos obrigatórios da política aparecem pendentes.
6. Como **Ana**: entregar documentos e registrar atividades.
7. Como **Bruno Lima**: o painel não mostra o processo da Ana, e a URL direta dá acesso negado (RNF01).
8. Como **Profa. Carla**: vê o estágio, mas não os dados da candidatura. Como **Prof. Diego**: acesso negado.
9. Reiniciar com `python3 src/main.py --falhar-aviso`; como **Coordenação**, encerrar o estágio. O encerramento fica registrado e a tela mostra "aviso ao estudante pendente".

## Testes

`python3 -m unittest discover -s tests -t .`

| Arquivo | O que cobre |
|---|---|
| `test_dominio.py` | regras de `Vaga`, `Candidatura`, `Estagio`, `Documento`, `Atividade` |
| `test_politica.py` | quem decide cada etapa e o recorte de cada papel |
| `test_casos_de_uso.py` | casos de uso com repositório em memória e notificador falso, sem banco nem servidor |
| `test_contratos.py` | os mesmos testes contra o dublê e a implementação real do repositório e do notificador |
| `test_web.py` | rotas de ponta a ponta e a tradução de erro em status HTTP |
| `test_arquitetura.py` | direção das dependências entre camadas, lida dos `import` |

## Acréscimos em relação à documentação

Para a interface ser usável, o protótipo tem quatro coisas que os documentos não listavam. Todas já estão na [arquitetura](arquitetura.md):

- tela inicial (`GET /`) com vagas e processos, pelo caso de uso `ListarPainel`, que reaproveita `ConsultarSituacao` (o RNF01 continua num ponto só);
- `LeituraSituacao.listar_vagas()` e `listar_candidaturas()`, para essa tela;
- `RepositorioProcesso.buscar_estagio_da_candidatura()`, para impedir a segunda homologação da mesma candidatura;
- login simples (`GET/POST /login`, `POST /logout`) com `CadastroUsuarios` em `infraestrutura/identidade/`.

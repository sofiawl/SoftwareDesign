# Histórico de alterações de coerência

Cada parte da documentação foi escrita por um integrante. Este arquivo registra as correções feitas para que os documentos conversem entre si, depois que o grupo definiu a arquitetura como **monólito modular em camadas com MVC**.

## Vocabulário adotado

Estes termos passam a valer em todos os documentos:

| Termo | Significado |
|---|---|
| Camada de apresentação (MVC) | *Controller* recebe a requisição, identifica o solicitante, chama o caso de uso e escolhe a *View*. *View* exibe o que recebe, sem filtrar dado. *Model* são as camadas de aplicação e domínio. |
| Camada de aplicação | Casos de uso, um por operação. Define as interfaces `RepositorioProcesso`, `LeituraSituacao` e `Notificador`. |
| Camada de domínio | Entidades, regras e política do regulamento. Não conhece tela, banco nem canal. |
| Camada de infraestrutura | Implementa as interfaces da aplicação (repositório persistente, notificador simulado). |
| Módulos | Vagas, Estágio, Acompanhamento e Política de estágio. Atravessam as camadas. |
| Interface | Substitui "porta" do vocabulário hexagonal. |
| Implementação / infraestrutura | Substitui "adaptador". |

## Alterações

| # | Arquivo | O que mudou | Por quê | Commit |
|---|---|---|---|---|
| 1 | `adr/ADR-01.md` | Decisão passa de "monólito com arquitetura hexagonal" para "monólito modular em camadas com MVC". Hexagonal vira alternativa rejeitada; a alternativa em camadas rejeitada passa a ser a versão sem módulos. Repositório e notificador continuam como interfaces da aplicação implementadas na infraestrutura. | O ADR decidia uma arquitetura diferente da escolhida pelo grupo e rejeitava justamente o monólito em camadas. | `64e8b9f` |
| 2 | `adr/ADR-02.md` | Documento recusado passa a ficar `RECUSADO` com motivo, em vez de "voltar a pendente". O registro do processo é explicitado como duas raízes (`Vaga` e `Estagio`). "Porta" e "núcleo" trocados por interface da aplicação e domínio. | Contradizia o RF05 (estado recusado) e o modelo de domínio. | `c5f78ce` |
| 3 | `adr/ADR-03.md` | Contexto e forças passam a citar os cinco eventos e os quatro casos de uso que avisam (antes falavam em "quatro momentos" e "três atos"). A decisão passa a dizer que o caso de uso grava um `AvisoPendente` pelo repositório quando o aviso falha. "Porta" e "adaptador" trocados por interface e implementação. | O ADR se contradizia na contagem de eventos e não dizia onde o aviso pendente fica, ponto que o modelo de domínio havia deixado para o grupo confirmar. | `b5ab5df` |
| 4 | `requisitos.md` | Nos ASRs, "núcleo", "porta" e "adaptador" trocados por domínio, interface e implementação. ASR2 passa a citar os quatro casos de uso que avisam (antes, três). ASR3 passa a dizer que o recorte acontece no caso de uso da consulta e que Controller e View não filtram. | Alinhar os ASRs ao ADR-01 e ao ADR-03, e ligar o ASR3 à camada MVC. | `d985104` |
| 5 | `modelo-dominio.md` | Introdução cita a arquitetura em camadas com MVC. Nova seção "Apresentação (MVC)" com os Controllers, o que cada um chama e as responsabilidades de Controller, View e Model. GRASP diferencia o Controller GRASP (caso de uso) do Controller MVC. Grafo de dependências e tabela de coesão ganham apresentação e infraestrutura. "Porta", "núcleo" e "adaptador" trocados. Seção 6 deixa de ser "pontos para confirmar" e registra o que foi alinhado nos ADRs. | O modelo descrevia a arquitetura hexagonal e não tinha a camada de apresentação. Os pontos 1 a 3 da seção 6 foram resolvidos nos itens 2 e 3. | `c5ed66f` |
| 6a | `modelo-dominio.md` | `SituacaoProcesso` volta ao módulo política (domínio), junto de `SituacaoVisivel`. | No item 5 ela foi para a aplicação, mas quem a consome é o `RecortePorPapel`, no domínio: o domínio passaria a depender da aplicação. O diagrama de componentes já a colocava em Política. | `575c3af` |
| 6b | `diagramas/componentes.puml` | Reescrito nas camadas Apresentação (MVC), Aplicação, Domínio e Infraestrutura. Entram Controllers e Views. Interfaces passam do pacote "Portas" para a Aplicação. `PoliticaRegulamentoVigente` aparece no Domínio. Notas sobre o Controller e sobre a regra das camadas. | O diagrama seguia núcleo, portas e adaptadores e não tinha a camada de apresentação. | `491d086` |
| 6c | `diagramas/componentes.puml`, `componentes.png` | Setas com direção explícita para as camadas aparecerem empilhadas; notas viram legenda. PNG adicionado ao repositório. | O layout automático colocava a infraestrutura no topo, sobre a composição, e escondia a ordem das camadas. | `e443f75` |
| 7 | `diagramas/classes.puml`, `classes.png` | Entra `EstagioController` (apresentação) chamando `HomologarEstagio`. `PoliticaRegulamentoVigente` passa de infraestrutura para domínio. Legenda com cinco cores. PNG regenerado. | O diagrama não mostrava a entrada pelo MVC e classificava a política do regulamento como infraestrutura, ao contrário do modelo de domínio. | `9b780bd` |
| 8 | `diagramas/sequencia.puml`, `sequencia.png` | Entram `EstagioController` e `View`: o fluxo começa no Controller, que monta o `Solicitante`, e os três finais (erro, sucesso, aviso pendente) voltam pela View. `podeDecidir` passa a receber `solicitante.papel` em vez do papel fixo. PNG adicionado. | O ator chamava o caso de uso direto, sem a camada MVC, e o papel fixo esvaziava a checagem de permissão. | `8eec452` |
| 9 | `diagramas/comunicacao.md` | Ganha título. Entram `SituacaoController` e `TelaSituacao`. Retornos passam a ir na própria mensagem (`x := op()`) e a numeração aninhada (1.1.1, 1.1.2) mostra que o caso de uso chama leitura e recorte. Cada objeto indica a camada. Texto diz que Controller e View não filtram. | Sem título e sem a camada MVC; retornos numerados como mensagens. | `240b9f5` |
| 10 | `README.md` | Informa a arquitetura escolhida logo após a pergunta central, com link para o ADR-01 e para este histórico. Separação de tarefas ganha links para os documentos de cada integrante. Corrige "coódigo-fonte". | O README não dizia qual arquitetura foi escolhida e só parte das tarefas apontava para seus arquivos. | `3bb7385` |
| 11 | `arquitetura.md`, `prototipo.md` | Entram o que o protótipo precisou e o documento não listava: `ListarPainel` e a rota `GET /`, rotas de login e logout, `buscarEstagioDaCandidatura`, `listarVagas`, `listarCandidaturas` e `CadastroUsuarios` em `infraestrutura/identidade/`. Árvore de pastas atualizada (`main.py`, arquivos de apoio da aplicação). A frase sobre permissão passa a dizer que, fora das quatro etapas da política, o caso de uso confere papel e vínculo. | Manter a proposta arquitetural igual ao código. A frase antiga dizia que toda checagem passava por `podeDecidir`, o que não valia para as operações do estudante e da concedente. | `abd7830` |
| 12 | `modelo-dominio.md` | Diagrama e tabela de interfaces ganham `buscarEstagioDaCandidatura`, `listarVagas` e `listarCandidaturas`. Entra o caso de uso `ListarPainel`, chamado pelo `SituacaoController`, que passa cada processo por `ConsultarSituacao`. GRASP Controller passa a falar em dez operações; SOLID (I) inclui o `ListarPainel`. | O modelo ficou atrás da arquitetura depois do item 11. | `79ff1f1` |
| 13 | `repositorio_persistente.py`, `tests/dubles.py`, `tests/test_contratos.py`, `tests/test_casos_de_uso.py`, `main.py`, `tests/test_web.py`, `prototipo.md`, `views/`, `situacao_controller.py`, `arquitetura.md`, `modelo-dominio.md` | O repositório persistente e o dublê gravam `AvisoPendente` (aviso, motivo e data), e o contrato RNF03 lê o pendente de volta nos dois. A semente inclui uma vaga encerrada da Empresa Beta, com teste `409` e um passo no roteiro. As views foram para `vagas/`, `estagio/`, `acompanhamento/` e `situacao/`. A árvore lista `LoginController`, `sessao.py`, `web.py` e `layout, erros, login`. O roteiro do modelo confere permissão por `podeDecidir` nas quatro etapas e por papel e vínculo nas demais. O `303` de sucesso vai à situação, ou ao painel ao cadastrar vaga. | O código e os documentos divergiam: `AvisoPendente` não entrava na gravação, a vaga encerrada não aparecia no demo, as views estavam planas, e duas frases descreviam a checagem de permissão e o redirecionamento de um jeito que o código não faz. | não commitado |

## Documentos criados

Documentos que estavam vazios ou não existiam, escritos já com o vocabulário acima.

| Arquivo | Conteúdo | Commit |
|---|---|---|
| `arquitetura.md` | Proposta arquitetural: camadas, módulos, estrutura de pastas, interfaces com contrato, comunicação, persistência (SQLite e esquema), integrações externas, decisões de comunicação, rotas HTTP e rastreabilidade dos ASRs. | `5b9548b` |
| `tradeoffs.md` | Comparação da arquitetura escolhida com camadas sem módulos, microsserviços e hexagonal, nos nove critérios do enunciado, com justificativa por critério e a decisão. | `924361f` |
| `evolucao.md` | Análise de evolução: notificador para e-mail, SQLite para PostgreSQL, relatório parcial (ASR1, com a decisão de não retroagir) e nova API REST; elementos afetados e inalterados e decisões que ajudam ou dificultam. | `14d51c7` |

## Protótipo

Código em `src/` e testes em `tests/`, seguindo a [proposta arquitetural](arquitetura.md). Como executar e roteiro de demonstração em [prototipo.md](prototipo.md).

| Commit | Conteúdo |
|---|---|
| `7739b20` | Domínio: `Vaga`, `Candidatura`, `Estagio`, `Documento`, `Atividade`, `PoliticaEstagio`, `RecortePorPapel` e modelos de leitura. Não importa nenhuma outra camada. |
| `eb116b9` | Aplicação: os nove casos de uso, `ListarPainel`, as interfaces `RepositorioProcesso`, `LeituraSituacao` e `Notificador`, e o aviso depois de gravar com `AvisoPendente`. |
| `843f1ee` | Infraestrutura: `RepositorioPersistente` sobre SQLite (esquema da arquitetura), `NotificadorSimulado` que pode falhar e `CadastroUsuarios`. |
| `11a8cef` | Apresentação MVC (Controllers, Views, sessão e servidor HTTP) e composição em `main.py`. |
| `b58dcf1` | Testes: domínio, política, casos de uso com dublês, contratos (dublê e implementação real), rotas HTTP e direção das dependências entre camadas. |
| `5673df0` | README com instruções de execução, `prototipo.md` e `.gitignore`. |

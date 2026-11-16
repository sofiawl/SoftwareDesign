# Análise de evolução

**Pergunta:** se uma das principais tecnologias ou integrações precisasse ser substituída, quais partes do sistema seriam afetadas?

Este documento analisa quatro mudanças sobre a arquitetura da [proposta arquitetural](arquitetura.md) (monólito modular em camadas com MVC, [ADR-01](adr/ADR-01.md)). As duas primeiras são trocas de tecnologia ou integração, como pede o enunciado. A terceira é a mudança de regulamento prevista no [ASR1](requisitos.md#asr1). A quarta é uma nova forma de acesso ao sistema.

Para cada mudança: o que muda, quais elementos são afetados, quais permanecem inalterados, e quais decisões arquiteturais ajudam ou dificultam.

## Resumo

`●` alterado, `+` acrescentado, `—` inalterado.

| Elemento | 1. E-mail | 2. PostgreSQL | 3. Relatório parcial | 4. API REST |
|---|---|---|---|---|
| Views | — | — | — | — |
| Controllers (MVC) | — | — | — | + (Controllers REST) |
| Casos de uso | — | — | — | — |
| Interfaces da aplicação | — | — | — | — |
| Entidades do domínio | — | — | — | — |
| `PoliticaRegulamentoVigente` | — | — | ● | — |
| `RepositorioPersistente` | — | ● | — | — |
| Esquema do banco | — | ● (dialeto) | — | — |
| `NotificadorSimulado` / novo notificador | + | — | — | — |
| Composição (`Main`) e configuração | ● | ● | — | ● |
| Testes de contrato | + (nova implementação) | + (nova implementação) | — | — |

Nenhuma das quatro mudanças altera caso de uso nem entidade do domínio. É o efeito esperado das três decisões que separam o que varia: `PoliticaEstagio` (ASR1), `Notificador` (ASR2) e `RepositorioProcesso` / `LeituraSituacao` ([ADR-01](adr/ADR-01.md), [ADR-02](adr/ADR-02.md)).

## Mudança 1 – Notificador simulado substituído por e-mail institucional

**O que muda.** A instituição libera o servidor de e-mail (SMTP). O aviso do RF09 deixa de ser simulado e passa a ser um e-mail real ao estudante.

**Elementos afetados:**

- **Infraestrutura:** nova classe `NotificadorEmail`, que implementa `Notificador`. Ela monta o e-mail a partir do `TipoEvento` e do motivo, busca o endereço do destinatário na tabela `usuario` e envia. Erro de conexão, timeout ou recusa do servidor viram `falha(motivo)`, nunca exceção.
- **Composição:** o `Main` passa a instanciar `NotificadorEmail` em vez de `NotificadorSimulado`.
- **Configuração:** endereço do servidor, credenciais e tempo máximo de espera.
- **Testes:** os testes de contrato do `Notificador` passam a rodar também contra `NotificadorEmail` (com um servidor SMTP de teste).

**Permanecem inalterados:**

- os quatro casos de uso que avisam (`DecidirCandidatura`, `HomologarEstagio`, `RecusarDocumento`, `EncerrarEstagio`);
- a interface `Notificador`, `Aviso`, `TipoEvento`, `ResultadoAviso` e `AvisoPendente`;
- domínio, Controllers, Views, repositório e esquema do banco.

**Decisões que ajudam:**

- [ADR-03](adr/ADR-03.md): o caso de uso conhece só a interface, e a chama depois de gravar. A ordem "gravar, depois avisar" não depende do canal.
- `ResultadoAviso` sem exceção: o caso de uso já trata a falha (grava `AvisoPendente`), qualquer que seja o canal.
- `TipoEvento` enumerado: o texto do e-mail é montado na implementação, a partir do tipo. Nenhum caso de uso monta frase.
- A tabela `usuario` já guarda o e-mail ([proposta arquitetural](arquitetura.md#5-persistência)).

**Decisões que dificultam ou riscos:**

- A chamada é **síncrona**: um servidor de e-mail lento atrasa a resposta da homologação. É preciso configurar um tempo máximo; ao estourar, a implementação devolve `falha` e o aviso fica pendente.
- O simulado não exercitou credencial, timeout real nem envio duplicado ([ADR-03](adr/ADR-03.md), consequências negativas). Os testes de contrato precisam cobrir esses casos antes da troca.
- Se o aviso passar a ser obrigação legal com garantia de entrega, a troca não é só de implementação: um ADR novo adota outbox. A interface e os casos de uso continuam; muda a garantia.

## Mudança 2 – SQLite substituído por PostgreSQL

**O que muda.** O protótipo usa SQLite num arquivo. Para atender várias réplicas da aplicação ou ter backup gerenciado, o banco passa a ser um servidor PostgreSQL.

**Elementos afetados:**

- **Infraestrutura:** `RepositorioPersistente` troca o driver e ajusta o SQL ao dialeto (tipos de data, geração de id, sintaxe de *upsert*). Isso inclui a consulta com junção de `LeituraSituacao.carregar`.
- **Esquema:** o script de criação é reescrito no dialeto do PostgreSQL. As tabelas e colunas são as mesmas.
- **Migração de dados:** script único que copia as tabelas do arquivo SQLite para o servidor.
- **Composição e configuração:** `Main` recebe a conexão do servidor (endereço, usuário, senha).
- **Implantação:** passa a existir um servidor de banco para instalar, monitorar e fazer backup.
- **Testes:** os testes de contrato do repositório passam a rodar também contra o PostgreSQL.

**Permanecem inalterados:**

- as interfaces `RepositorioProcesso` e `LeituraSituacao`;
- todos os casos de uso, o domínio, a política, Controllers e Views;
- o notificador.

**Decisões que ajudam:**

- [ADR-01](adr/ADR-01.md): o banco só é acessado pela infraestrutura, atrás das interfaces da aplicação. Nenhum caso de uso tem SQL.
- [ADR-02](adr/ADR-02.md): um repositório só. A troca é de uma classe, não de vários repositórios espalhados por módulo.
- Segregação de interfaces com a mesma implementação: `RepositorioProcesso` e `LeituraSituacao` mudam juntos, numa classe.
- Contrato "grava a raiz inteira ou nada": define o que a nova implementação precisa garantir (transação por raiz), e o teste de contrato confere.
- `documento.tipo` como dado, não como coluna: o esquema não tem nada específico do regulamento para migrar.

**Decisões que dificultam ou riscos:**

- Se algum caso de uso chamar SQL direto (o risco de "interface vazia" do [ADR-01](adr/ADR-01.md)), ele quebra na troca. A revisão da direção dos imports é o que evita isso.
- A junção de `LeituraSituacao` é o SQL mais complexo e o mais sensível ao dialeto.
- Com várias réplicas, duas requisições podem alterar a mesma raiz ao mesmo tempo (duas decisões sobre a mesma vaga). No SQLite isso não aparecia, porque a escrita é serializada. Passa a ser preciso controle de concorrência (versão na raiz ou bloqueio na transação), dentro da implementação do repositório.

## Mudança 3 – regulamento passa a exigir relatório parcial (ASR1)

**O que muda.** A coordenação passa a exigir um **relatório parcial** além do termo de compromisso, do plano de atividades e do relatório. Variação do mesmo cenário: o regulamento passa a deixar o **orientador** recusar o relatório, em vez da coordenação.

**Elementos afetados:**

- **Domínio:** `PoliticaRegulamentoVigente` acrescenta `RELATORIO_PARCIAL` à lista de `documentosObrigatorios()`. Na variação, `podeDecidir(RECUSA_DOCUMENTO, ORIENTADOR)` passa a responder `true` para o relatório.
- **Testes:** os testes da política recebem o caso novo.

**Permanecem inalterados:**

- `Estagio`, `Documento`, `Candidatura` e `Atividade`;
- `Candidatar`, `HomologarEstagio`, `EntregarDocumento`, `RecusarDocumento`, `RegistrarAtividade` e `EncerrarEstagio`: eles perguntam à política e funcionam para qualquer tipo;
- o esquema do banco: o relatório parcial é uma linha nova em `documento`, com `tipo = RELATORIO_PARCIAL`;
- as Views: a tela de situação lista os documentos que o estágio tem, sem tipos fixos;
- as rotas: `/estagios/{id}/documentos/{tipo}/...` já recebem o tipo como parâmetro.

**Estágios já homologados.** O estágio recebe a lista vigente **no momento da homologação** e a guarda como seus documentos ([modelo de domínio](modelo-dominio.md#módulo-estágio)). A decisão é:

- **por padrão, a regra nova não retroage.** Os estágios homologados antes da mudança continuam com os três documentos. É como o termo de compromisso: vale o regulamento da época em que foi assinado. Nenhum dado existente muda;
- **se o regulamento exigir retroação**, entra uma operação nova: `Estagio.exigirDocumento(tipo)`, que acrescenta um `Documento PENDENTE`, e o caso de uso `ExigirDocumento`, executado pela coordenação. É um acréscimo ao módulo Estágio, que não altera nenhuma operação existente.

**Decisões que ajudam:**

- [ADR-01](adr/ADR-01.md): a política é um lugar único, no domínio. Os casos de uso perguntam, não repetem a lista.
- [ADR-02](adr/ADR-02.md): documento é um item com tipo e estado no processo, não uma etapa nova nem um filtro novo.
- `TipoDocumento` como valor definido pela política, não `enum` espalhado nos casos de uso ([modelo de domínio](modelo-dominio.md#módulo-política-de-estágio)).
- `podeDecidir(etapa, papel)` com `ORIENTADOR` já previsto em `Papel`: mudar quem aprova é mudar a resposta, não a pergunta.

**Decisões que dificultam ou riscos:**

- Se uma View listar os documentos com nomes fixos ("Termo", "Plano", "Relatório") em vez de iterar o que recebe, ela não mostra o relatório parcial. A regra "View exibe o que recebe" evita isso.
- Uma regra futura como "só encerra com todos os documentos entregues" passaria a depender da lista do estágio, e não da política vigente, por causa da decisão de não retroagir. Isso precisa estar explícito quando a regra for criada.

## Mudança 4 – nova interface: aplicativo ou API REST

**O que muda.** A instituição quer que o estudante registre atividades por um aplicativo de celular, que consome uma API REST em JSON. A interface web continua.

**Elementos afetados:**

- **Apresentação:** novos Controllers REST (por exemplo, `AcompanhamentoApiController`, `SituacaoApiController`) que recebem JSON, montam o `Solicitante` a partir de um token e chamam os **mesmos** casos de uso. A resposta é JSON em vez de uma View HTML.
- **Autenticação:** o aplicativo não usa a sessão do navegador; a apresentação passa a aceitar token. Só a montagem do `Solicitante` muda.
- **Composição:** registra as rotas novas.
- **Documentação de API:** as rotas JSON entram na [proposta arquitetural](arquitetura.md#8-rotas-http).

**Permanecem inalterados:**

- todos os casos de uso, o domínio, a política e o `RecortePorPapel`;
- repositório, notificador e banco;
- os Controllers e Views web existentes.

**Decisões que ajudam:**

- Controller sem regra de negócio ([ADR-01](adr/ADR-01.md)): a regra está nos casos de uso, então o Controller REST só traduz entrada e saída.
- O recorte do RNF01 acontece no caso de uso `ConsultarSituacao` ([ASR3](requisitos.md#asr3)), não na View: o JSON do aplicativo já sai recortado, sem reimplementar o filtro.
- O caso de uso recebe o `Solicitante` pronto e não sabe se veio de sessão ou de token.

**Decisões que dificultam ou riscos:**

- Se alguma regra tiver vazado para um Controller web (o risco de "Controller gordo" do [ADR-01](adr/ADR-01.md)), ela não existe no caminho REST, e o aplicativo aceita o que a tela recusaria.
- O MVC renderizado no servidor não tinha contrato de API versionado. Com um cliente externo, mudar o formato da resposta passa a exigir versionamento das rotas JSON.

## Conclusão

As quatro mudanças ficam contidas em uma camada ou num ponto do domínio:

- tecnologia (banco, canal de aviso) → **infraestrutura** e composição;
- regulamento → **`PoliticaRegulamentoVigente`**;
- forma de acesso → **apresentação**.

O que torna isso possível são decisões tomadas antes das mudanças: interfaces só onde há variação prevista (ADR-01, ADR-03), um repositório único com documento como dado (ADR-02), e a disciplina de Controller sem regra e View sem filtro. O que pode atrapalhar é sempre a quebra dessa disciplina: SQL num caso de uso, regra num Controller, tipo de documento fixo numa View. Por isso a revisão do protótipo deve conferir a direção dos imports e não só os nomes das pastas.

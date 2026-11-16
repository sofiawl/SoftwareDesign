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
| 6b | `diagramas/componentes.puml` | Reescrito nas camadas Apresentação (MVC), Aplicação, Domínio e Infraestrutura. Entram Controllers e Views. Interfaces passam do pacote "Portas" para a Aplicação. `PoliticaRegulamentoVigente` aparece no Domínio. Notas sobre o Controller e sobre a regra das camadas. | O diagrama seguia núcleo, portas e adaptadores e não tinha a camada de apresentação. | este commit |

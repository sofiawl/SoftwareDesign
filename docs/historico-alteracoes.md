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

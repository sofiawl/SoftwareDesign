# Descrição do problema e requisitos

## Contexto

O estágio liga o estudante, a concedente e a instituição de ensino. Hoje o acompanhamento fica em planilha, e-mail e documento avulso. O sistema reúne, num único lugar, a vaga, a candidatura, a aprovação, o orientador, os documentos e as atividades.

## Atores

- **Concedente:** cadastra vaga e aceita ou recusa candidatura.
- **Estudante:** candidata-se, entrega documentos, registra atividades e consulta o próprio processo.
- **Coordenação de estágios:** homologa o estágio, designa orientador, recusa documento e encerra o estágio.
- **Orientador:** consulta os estágios sob sua orientação.

## Requisitos funcionais

- RF01: O sistema deve permitir que a concedente cadastre uma vaga com área, carga horária semanal, período e pré-requisitos. A vaga inicia aberta.
- RF02: O sistema deve permitir que o estudante se candidate a uma vaga aberta. O sistema recusa candidatura para vaga encerrada e segunda candidatura do mesmo estudante à mesma vaga.
- RF03: O sistema deve permitir que a concedente aceite ou recuse uma candidatura. A recusa só é registrada com motivo. Candidatura recusada não gera estágio.
- RF04: O sistema deve permitir que a coordenação homologue uma candidatura aceita e vincule um orientador. A homologação cria o estágio. Candidatura que não foi aceita não pode ser homologada.
- RF05: O sistema deve controlar os documentos do estágio (termo de compromisso, plano de atividades e relatório), cada um no estado pendente, entregue ou recusado. A recusa só é registrada com motivo.
- RF06: O sistema deve permitir que o estudante registre atividade com data, descrição e carga horária somente em estágio em andamento.
- RF07: O sistema deve exibir a situação do estágio, com vaga, candidatura, homologação, orientador, documentos e atividades.
- RF08: O sistema deve permitir que a coordenação encerre o estágio informando o motivo. Estágio encerrado não aceita atividade nova.
- RF09: O sistema deve avisar o estudante quando a candidatura é aceita ou recusada, quando o estágio é homologado, quando um documento é recusado e quando o estágio é encerrado.

## Restrições

- RNF01: O sistema deve exibir dados pessoais do estudante (identidade, documentos e atividades) somente a quem pode recebê-los: o próprio estudante, o orientador dos estágios dele, a concedente das vagas em que ele se candidatou e a coordenação de estágios.
- RNF02: O sistema deve manter vaga, candidatura, estágio, documento e atividade após o reinício.
- RNF03: O sistema deve manter a decisão já registrada quando o aviso do RF09 falhar, e deve marcar esse aviso como pendente.
- RNF04: O protótipo deve executar o RF09 sem serviço real da instituição. O canal inicial pode ser simulado.

## Requisitos arquiteturalmente significativos

Decisões em [docs/adr/](adr/).

### ASR1

O sistema deve permitir incluir ou retirar um documento obrigatório, ou mudar quem aprova uma etapa, sem alterar candidatura, registro de atividade nem armazenamento.

Por que influencia a arquitetura: o regulamento muda o que a coordenação exige no processo (termo de compromisso, plano de atividades, relatório, e depois um relatório parcial) e quem decide cada etapa (a concedente na candidatura, a coordenação na homologação). Se essa lista morar em candidatar, entregar documento, encerrar e em colunas fixas do banco, um documento novo altera os quatro lugares. A decisão é uma política só, no núcleo. Os casos de uso perguntam quais documentos são obrigatórios e quem pode aprovar. No processo, cada documento é um item com tipo e estado, não uma etapa nova ([ADR-02](adr/ADR-02.md)).

A política fica no núcleo e o banco fica fora, senão o relatório parcial atravessa candidatura, entrega, encerramento e o esquema. [ADR-01](adr/ADR-01.md).

### ASR2

O sistema deve permitir trocar o canal do aviso do RF09 (simulado, e-mail, REST ou SOAP) sem alterar o registro da decisão.

Por que influencia a arquitetura: o estudante é avisado quando a candidatura é aceita ou recusada, quando o estágio é homologado, quando um documento é recusado e quando o estágio é encerrado. O protótipo não fala com o serviço da instituição (RNF04). Se homologar, recusar e encerrar abrirem a conexão HTTP, trocar o simulado por e-mail reescreve os três casos de uso. A decisão de negócio já está gravada (RNF03): a concedente aceitou, ou a coordenação homologou, mesmo que o aviso não saia.

A decisão é uma porta de aviso, chamada depois de gravar. O caso de uso não conhece o canal. O adaptador desta entrega é o simulado. [ADR-03](adr/ADR-03.md).

### ASR3

O sistema deve aplicar o RNF01 uma única vez, na consulta do RF07.

Por que influencia a arquitetura: a situação do estágio junta vaga, candidatura, homologação, orientador, documentos e atividades. Os quatro papéis do RNF01 não veem o mesmo recorte. A concedente precisa do nome de quem se candidatou à vaga dela, e não vê atividade de um estágio em outra concedente nem documento de um processo que não é seu. O orientador vê documentos e atividades dos estágios que orienta, não o conjunto da coordenação. O estudante vê só o próprio processo. Se cada tela, cada serviço ou cada leitura direta ao banco aplicar o próprio filtro, um deles entrega documento ou atividade a mais.

A decisão é um ponto só, na entrada da consulta: a leitura junta os dados e o RNF01 corta o resultado. Isso precisa acontecer no mesmo processo. Se cada tela ou cada ator ler o banco por conta própria, o recorte diverge. [ADR-01](adr/ADR-01.md).

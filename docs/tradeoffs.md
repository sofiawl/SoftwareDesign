# Alternativas e trade-offs

Este documento compara a arquitetura escolhida, **monólito modular em camadas com MVC** ([ADR-01](adr/ADR-01.md)), com três alternativas. As alternativas são as mesmas consideradas no ADR-01; aqui elas são comparadas critério a critério.

## 1. As alternativas

**A. Monólito modular em camadas com MVC (escolhida).** Um processo. Camadas apresentação (MVC), aplicação, domínio e infraestrutura; módulos Vagas, Estágio, Acompanhamento e Política atravessando as camadas. Repositório e notificador como interfaces da aplicação, implementadas na infraestrutura. Detalhes na [proposta arquitetural](arquitetura.md).

**B. Monólito em camadas sem módulos.** Um processo, pastas `controllers/`, `services/`, `repositories/`. Cada serviço grava no banco e chama o canal de aviso diretamente. A lista de documentos obrigatórios e o filtro de quem vê o quê ficam onde forem usados.

**C. Microsserviços por ator.** Um serviço para concedente (vagas e candidaturas), um para estudante (documentos e atividades), um para coordenação (homologação e encerramento) e um para orientador (consulta). Cada serviço com seu banco, comunicando por REST.

**D. Monólito hexagonal (portas e adaptadores).** Um processo. O núcleo (domínio e casos de uso) fica isolado de toda entrada e saída: telas, banco e aviso são adaptadores, cada um atrás de uma porta.

## 2. Comparação

Escala: `++` muito favorável, `+` favorável, `0` neutro, `−` desfavorável, `−−` muito desfavorável. A nota é relativa às outras alternativas, para o tamanho e os requisitos deste sistema.

| Critério | A. Camadas + MVC (escolhida) | B. Camadas sem módulos | C. Microsserviços | D. Hexagonal |
|---|---|---|---|---|
| Modificabilidade | `+` | `−` | `−` | `+` |
| Desempenho | `+` | `+` | `−` | `+` |
| Disponibilidade | `0` | `−` | `0` | `0` |
| Testabilidade | `+` | `−` | `−` | `++` |
| Complexidade | `0` | `+` | `−−` | `−` |
| Implantação | `++` | `++` | `−−` | `++` |
| Escalabilidade | `0` | `0` | `++` | `0` |
| Custo de desenvolvimento | `0` | `+` | `−−` | `−` |
| Custo de operação | `+` | `+` | `−−` | `+` |

### Modificabilidade

As mudanças previstas são as dos ASRs: documento obrigatório novo ou aprovador diferente (ASR1) e canal de aviso diferente (ASR2).

- **A:** a regra do regulamento está em `PoliticaEstagio` e o canal atrás de `Notificador`. Um relatório parcial muda a política; um canal novo é uma implementação nova. Casos de uso, Controllers e banco ficam.
- **B:** a lista de documentos aparece em candidatar, entregar documento, encerrar e nas colunas do banco; o canal é chamado em quatro casos de uso. Cada mudança do ASR1 ou ASR2 edita vários lugares.
- **C:** uma mudança dentro de um serviço é isolada, mas as do ASR1 atravessam serviços: a lista de documentos e o filtro do RNF01 estão repetidos em cada um, e mudam juntos, com versionamento de API entre eles.
- **D:** mesmo resultado de A para as mudanças previstas. A vantagem extra do hexagonal (trocar a entrada por outra) também existe em A: uma API REST é um conjunto novo de Controllers chamando os mesmos casos de uso.

### Desempenho

- **A, B e D:** chamadas locais. A consulta de situação é uma leitura com junção no mesmo banco. As camadas e interfaces de A e D custam chamadas de método, irrelevantes perto do acesso ao banco.
- **C:** a situação junta dados de três ou quatro serviços pela rede a cada consulta. Latência somada e mais pontos de falha numa operação que é a mais usada (RF07).

### Disponibilidade

- **A e D:** um processo só; se cair, o sistema todo cai. A falha do canal de aviso, que é a dependência externa, não derruba a decisão: ela é gravada antes e o aviso fica pendente (RNF03).
- **B:** mesmo ponto único de falha, e o canal chamado dentro do serviço que grava torna fácil que uma falha de aviso desfaça ou interrompa a decisão, contrariando o RNF03.
- **C:** um serviço fora não derruba os outros, em tese. Mas a consulta de situação depende de todos, e a homologação depende do serviço de vagas para ler a candidatura. A disponibilidade de cada fluxo é a do serviço mais fraco que ele usa.

### Testabilidade

- **A:** cada caso de uso é testado com repositório em memória e notificador falso, sem banco e sem servidor. Controllers são finos e testados pela rota.
- **B:** a regra está no serviço que abre o banco e o canal; testar exige banco real ou dublê do driver.
- **C:** cada serviço é testável sozinho, mas os fluxos (candidatar → homologar → consultar) exigem testes de integração com vários serviços no ar e testes de contrato entre APIs.
- **D:** a melhor isolação: até a entrada é uma porta, e o núcleo é testado sem nenhum framework web.

### Complexidade

- **A:** quatro camadas, quatro módulos e três interfaces. Vocabulário conhecido pela equipe (MVC).
- **B:** a mais simples para começar: três pastas e chamadas diretas.
- **C:** quatro serviços, quatro bancos, API entre eles, consistência entre bancos (a candidatura aceita num, o estágio criado em outro), descoberta de serviço e observabilidade distribuída.
- **D:** porta e adaptador para cada entrada e saída, inclusive telas, e um vocabulário que a equipe ainda não usa.

### Implantação

- **A, B e D:** um artefato e um arquivo de banco (SQLite). Subir o protótipo é executar um processo.
- **C:** quatro serviços e quatro bancos para subir, configurar e versionar juntos, mais um gateway para a interface.

### Escalabilidade

- **A, B e D:** escala a aplicação inteira. Com SQLite, as escritas são limitadas a um processo; com um servidor de banco ([evolução](evolucao.md#mudança-2--sqlite-substituído-por-postgresql)), várias réplicas da aplicação atendem mais usuários. O volume de uma instituição de ensino (centenas de estágios por semestre) está longe desse limite.
- **C:** cada serviço escala separado. A vantagem só aparece com carga desigual entre atores, que não é o caso aqui.

### Custo de desenvolvimento

- **A:** custo inicial de desenhar as interfaces e os módulos antes do primeiro caso de uso; custo baixo nas mudanças previstas.
- **B:** começa mais barato e encarece a cada mudança do regulamento ou do canal.
- **C:** o mais caro: infraestrutura de comunicação, contratos de API e lógica duplicada (política e RNF01) em vários serviços, para uma equipe de quatro pessoas.
- **D:** mais caro que A pelas portas de entrada, que não trazem ganho para as mudanças previstas.

### Custo de operação

- **A, B e D:** um processo e um banco; o custo de manter um servidor pequeno.
- **C:** vários processos, bancos e monitoramento distribuído; precisa de alguém operando a plataforma.

## 3. Por que A

Os ASRs pesam mais que os outros critérios, porque são as mudanças que já se sabe que vão acontecer:

- **B** perde em modificabilidade justamente no ASR1 e no ASR2, e coloca o RNF03 em risco.
- **C** quebra o ASR3: a situação junta dados de vários serviços, e o filtro do RNF01 teria de ser repetido em cada um. O ganho em escalabilidade não tem uso no volume do sistema, e o custo de operação é o maior.
- **D** atende os três ASRs tão bem quanto A e testa um pouco melhor. A diferença está nas portas de entrada, que custam complexidade e desenvolvimento sem cobrir nenhuma mudança prevista. A tem o mesmo ganho onde ele importa (banco e aviso) e usa o MVC que a equipe já conhece.

O que A abre mão, conscientemente:

- **escalar por ator**, que C daria;
- **isolar o núcleo de toda entrada**, que D daria; em A, isso depende da disciplina de manter o Controller sem regra (risco registrado no [ADR-01](adr/ADR-01.md)).

## 4. Outras alternativas descartadas em outros ADRs

- **Pipes and filters e arquitetura orientada a eventos** para o fluxo do processo: descartadas no [ADR-02](adr/ADR-02.md), porque cada ato depende do estado atual do processo, não da saída do ato anterior.
- **Fila (pub/sub) para o aviso:** descartada no [ADR-03](adr/ADR-03.md), porque o que não pode se perder é a decisão, que já está gravada; o aviso que falha fica pendente.

## 5. Quando reavaliar

- Se o aviso virar requisito legal com garantia de entrega: adotar outbox, mantendo a interface `Notificador` ([ADR-03](adr/ADR-03.md)).
- Se o sistema passar a atender várias instituições com carga muito desigual entre módulos: extrair o módulo mais carregado como serviço. A fronteira de módulo de A é o ponto de corte, e a extração não muda os outros módulos.

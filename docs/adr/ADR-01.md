# ADR-01: Monólito modular em camadas com MVC

Status: aceita

## Contexto

O sistema precisa cadastrar vagas, receber candidaturas, homologar, designar orientador e controlar documentos e atividades.

Três requisitos puxam a estrutura: a regra de documentos e de aprovação muda sem varrer o código ([ASR1](../requisitos.md#asr1)), o aviso externo é substituível ([ASR2](../requisitos.md#asr2)) e a consulta de situação respeita o papel ([ASR3](../requisitos.md#asr3)).

## Problema e forças

- O protótipo cobre um fluxo: vaga, candidatura, homologação, orientador, documentos e atividades. Os dados sobrevivem ao reinício. O aviso ao estudante começa simulado.
- O regulamento muda o documento exigido e quem aprova a etapa. Candidatura, atividade e banco não devem mudar junto.
- O aviso muda de canal. Aceitar a candidatura e homologar o estágio não devem ser reescritos por isso.
- A situação junta vaga, candidatura, orientador, documento e atividade. Cada papel vê um recorte diferente desse mesmo processo.
- Quatro atores usam o sistema por telas. A equipe é pequena e conhece o padrão MVC.

## Alternativas consideradas

**Monólito em camadas sem módulos, com o caso de uso gravando no banco e enviando o aviso.** É o desenho natural de um fluxo curto: a regra fica perto da tabela, e as pastas são `controllers/`, `services/`, `repositories/`. A lista do que a coordenação exige (termo, plano, relatório) cabe ali. Ela quebra quando a coordenação inclui um relatório parcial, ou quando o aviso deixa de ser o simulado e passa a ser o da instituição. Homologar, recusar documento e encerrar são três atos diferentes, e os três passam a ser editados, porque cada um abre o banco e o canal. Sem módulos, vaga, estágio e documento ficam misturados em cada camada, e nada impede um serviço de mexer na tabela de outro.

**Microsserviços, um por ator.** Concedente, estudante, coordenação e orientador parecem quatro sistemas. A situação do estágio não é de um ator só. Para a coordenação encerrar, e para o orientador acompanhar, a leitura precisa de vaga, candidatura, documentos e atividades ao mesmo tempo. A regra de qual documento é obrigatório e o corte de quem vê dado pessoal seriam repetidos em cada serviço. A concedente, para aceitar a candidatura, dependeria de outro serviço só para ver o nome do estudante sem receber atividade de um estágio que não é dela.

**Monólito com arquitetura hexagonal (portas e adaptadores).** Um processo, com o núcleo isolado de toda entrada e saída: a tela também é um adaptador, e cada interação ganha uma porta. Atende os três ASRs, mas cobra uma porta e um adaptador para cada entrada, inclusive as telas, que não variam neste trabalho. As variações previstas são duas: armazenamento e canal de aviso. A equipe já organiza telas em MVC, e o hexagonal acrescentaria um vocabulário e uma camada de indireção que o protótipo não usa.

## Decisão

Adotar **monólito modular em camadas, com a camada de apresentação em MVC**.

Camadas, de cima para baixo:

- **Apresentação (MVC).** O *Controller* recebe a requisição, identifica o solicitante (id e papel), chama um caso de uso e escolhe a *View*. A *View* exibe o que recebe e não filtra dado. O *Model* do MVC são as camadas de aplicação e domínio. O Controller não tem regra de negócio e não acessa o banco.
- **Aplicação.** Um caso de uso por operação do sistema. Pergunta à política quem pode decidir, carrega, chama o domínio, grava e avisa. Define as interfaces de que precisa: `RepositorioProcesso`, `LeituraSituacao` e `Notificador`.
- **Domínio.** Entidades, regras e política do regulamento. Não conhece tela, banco nem canal.
- **Infraestrutura.** Implementa as interfaces da aplicação: o repositório persistente ([ADR-02](ADR-02.md)) e o notificador ([ADR-03](ADR-03.md)).

Cada camada só chama a de baixo. A exceção é a infraestrutura, que implementa interfaces definidas pela aplicação (inversão de dependência). Ela é usada só nas duas variações previstas, armazenamento e canal de aviso. A composição (ponto de entrada) escolhe a implementação concreta e a entrega aos casos de uso.

Módulos, que atravessam as camadas:

- **Vagas:** vaga e candidatura, inclusive a decisão da concedente.
- **Estágio:** homologação, orientador e encerramento. O estágio só existe após candidatura aceita e homologação.
- **Acompanhamento:** documentos e atividades do estágio, consultando a política do que é obrigatório.
- **Política de estágio:** lista de documentos obrigatórios, quem pode aprovar cada etapa e o recorte do que cada papel vê (ASR3). Os casos de uso perguntam; não duplicam a lista.

Um módulo não lê tabela nem altera objeto de outro. Comunicação entre módulos é chamada local. A única saída externa desta entrega é a interface de notificação.

## Consequências positivas

- Trocar banco ou aviso altera só a infraestrutura e a composição. Vaga, candidatura, estágio e os Controllers ficam.
- A política de documentos tem um lugar. Incluir um relatório parcial mexe nela, não no cadastro de atividade.
- O MVC separa tela de regra: uma tela nova é um Controller e uma View, sem duplicar regra nem o recorte do RNF01.
- Caso de uso testa com repositório e notificador falsos, sem subir servidor nem banco.
- Os módulos dão a cada parte do trabalho (modelo, UML, proposta, trade-offs) a mesma fronteira, para não se contradizer.

## Consequências negativas

- Mais interfaces do que um CRUD em três camadas. Parte delas existe para a troca futura, não para o primeiro fluxo.
- Uma requisição atravessa Controller, caso de uso, domínio e repositório, mesmo numa consulta simples.
- Chamada local entre módulos pode virar emaranhado se um módulo alcançar tabela ou objeto interno do outro.
- A equipe precisa manter as regras: Controller sem regra de negócio, View sem filtro, domínio sem import de infraestrutura. A ferramenta não impede o atalho.

## Custos e riscos

- Custo de desenho: quatro módulos, quatro camadas e três interfaces antes do primeiro caso de uso.
- Risco de Controller gordo: a regra migra para o Controller porque "é só um if". Ela some do domínio e não é testada pelos casos de uso.
- Risco de interfaces vazias: interface criada e o caso de uso chamando SQL mesmo assim. A revisão do protótipo deve olhar a direção do import, não só o nome da pasta.
- Risco de corte errado: se documento e atividade precisarem de transação com a homologação o tempo todo, o módulo Acompanhamento foi longe demais. A correção ainda é local (mover a fronteira no mesmo processo), o que é mais barato do que desfazer serviços separados.

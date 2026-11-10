# ADR-01: Monólito modular com portas e adaptadores

Status: aceita

## Contexto

O sistema precisa cadastrar vagas, receber candidaturas, homologar, designar orientador e controlar documentos e atividades. 

Três requisitos puxam a estrutura: a regra de documentos e de aprovação muda sem varrer o código ([ASR1](../requisitos.md#asr1)), o aviso externo é substituível ([ASR2](../requisitos.md#asr2)) e a consulta de situação respeita o papel ([ASR3](../requisitos.md#asr3)).

## Problema e forças

- O protótipo cobre um fluxo: vaga, candidatura, homologação, orientador, documentos e atividades. Os dados sobrevivem ao reinício. O aviso ao estudante começa simulado.
- O regulamento muda o documento exigido e quem aprova a etapa. Candidatura, atividade e banco não devem mudar junto.
- O aviso muda de canal. Aceitar a candidatura e homologar o estágio não devem ser reescritos por isso.
- A situação junta vaga, candidatura, orientador, documento e atividade. Cada papel vê um recorte diferente desse mesmo processo.

## Alternativas consideradas

**Monólito em camadas, com o caso de uso gravando no banco e enviando o aviso.** É o desenho natural de um fluxo curto: a regra fica perto da tabela. A lista do que a coordenação exige (termo, plano, relatório) cabe ali. Ela quebra quando a coordenação inclui um relatório parcial, ou quando o aviso deixa de ser o simulado e passa a ser o da instituição. Homologar, recusar documento e encerrar são três atos diferentes, e os três passam a ser editados, porque cada um abre o banco e o canal.

**Microsserviços, um por ator.** Concedente, estudante, coordenação e orientador parecem quatro sistemas. A situação do estágio não é de um ator só. Para a coordenação encerrar, e para o orientador acompanhar, a leitura precisa de vaga, candidatura, documentos e atividades ao mesmo tempo. A regra de qual documento é obrigatório e o corte de quem vê dado pessoal seriam repetidos em cada serviço. A concedente, para aceitar a candidatura, dependeria de outro serviço só para ver o nome do estudante sem receber atividade de um estágio que não é dela.

**Monólito com arquitetura hexagonal.** Um processo. A política de documentos e o corte de quem vê o processo ficam no núcleo. O banco e o aviso ficam fora. A consulta junta os dados na mesma execução e só então aplica o recorte do papel. Trocar o armazenamento ou o canal não reescreve candidatura, homologação nem atividade.

## Decisão

Adotar monólito com arquitetura hexagonal (portas e adaptadores).

Módulos do núcleo:

- **Vagas:** vaga e candidatura, inclusive a decisão da concedente.
- **Estágio:** homologação, orientador e encerramento. O estágio só existe após candidatura aceita e homologação.
- **Acompanhamento:** documentos e atividades do estágio, consultando a política do que é obrigatório.
- **Política de estágio:** lista de documentos obrigatórios e quem pode aprovar cada etapa. Os casos de uso perguntam; não duplicam a lista.

A aplicação é a borda em que o papel é checado (ASR3). Adaptadores ficam fora do núcleo: o repositório do processo ([ADR-02](ADR-02.md)) e a notificação ([ADR-03](ADR-03.md)). Quem sobe o processo escolhe o adaptador concreto. O núcleo recebe a porta.

Comunicação entre módulos é chamada local. A única saída externa desta entrega é a porta de notificação.

## Consequências positivas

- Trocar banco ou aviso não reescreve vaga, candidatura nem estágio.
- A política de documentos tem um lugar. Incluir um relatório parcial mexe nela, não no cadastro de atividade.
- Caso de uso testa com repositório e notificador falsos, sem subir infraestrutura.
- As outras seções do trabalho (modelo, UML, proposta, trade-offs) têm uma fronteira só para não se contradizer.

## Consequências negativas

- Mais interfaces do que um script com três tabelas. Parte da interface existe para a troca futura, não para o primeiro fluxo.
- Chamada local entre módulos pode virar emaranhado se um módulo alcançar tabela ou objeto interno do outro.
- A equipe precisa manter a regra: núcleo não importa adaptador. A ferramenta não impede o atalho.

## Custos e riscos

- Custo de desenho: quatro módulos e duas portas (repositório e notificação) antes do primeiro caso de uso.
- Risco de portas vazias: interface criada e o caso de uso chamando SQL mesmo assim. A revisão do protótipo deve olhar a direção do import, não só o nome da pasta.
- Risco de corte errado: se documento e atividade precisarem de transação com a homologação o tempo todo, o módulo Acompanhamento foi longe demais. A correção ainda é local (mover a fronteira no mesmo processo), o que é mais barato do que desfazer serviços separados.

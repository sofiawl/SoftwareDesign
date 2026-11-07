# ADR-02: O processo de estágio permanece num repositório

Status: aceita

## Contexto

O [ADR-01](ADR-01.md) deixou o armazenamento fora do núcleo. Não disse o que acontece com o processo depois de cada ato. A candidatura é aceita, a coordenação homologa, o documento volta recusado, e meses depois o estudante lança mais uma atividade no mesmo estágio. O orientador não lê a saída da última etapa. Lê a situação de agora ([RF07](../requisitos.md)).

## Problema e forças

- O estágio dura. O estudante volta ao mesmo processo. O documento recusado continua nele, em outro estado, e não segue para uma etapa seguinte.
- A situação é uma leitura desse processo, cortada uma vez pelo papel de quem pede.
- A atividade só existe com o estágio em andamento. A homologação só existe com a candidatura aceita. O ato seguinte depende do estado atual, não de quem chamou quem.
- Um documento obrigatório novo é mais um item nesse processo. Não é uma fase nova do fluxo.

## Alternativas consideradas

**Pipes and filters.** Cada ato é um filtro: candidatura, homologação, documentos, atividades, encerramento. A saída de um entra no próximo. O fluxo parece isso, porque a homologação só vem depois da candidatura aceita. Não é isso no uso. A atividade não é a saída da homologação: o estudante acrescenta outra no mesmo estágio, meses depois. O documento recusado não avança: volta a pendente. A concedente e o orientador não consomem a saída de um filtro. Precisam do processo como ele está.

**Repository.** Um registro do processo no centro. Candidatar, homologar, entregar documento, lançar atividade e encerrar leem esse registro, aplicam a regra e gravam de volta. Ninguém passa o processo adiante. A situação é o próprio registro. Termo, plano, relatório e um relatório parcial futuro são itens com tipo e estado ali, não filtros novos.

## Decisão

Adotar o estilo repository para o processo de estágio.

O registro guarda a vaga, as candidaturas e, quando passa a existir, o estágio: orientador, documentos, atividades e encerramento. Documento e atividade não formam outro repositório. Mudam o mesmo processo.

O acesso continua pela porta do ADR-01. Este ADR não escolhe produto de banco. Escolhe que existe um estado só, e que cada ato depende dele.

## Consequências positivas

- "Atividade só em estágio em andamento" olha o estado, num lugar.
- A consulta de situação não monta o processo juntando a saída de cada etapa.
- Incluir um relatório parcial não cria filtro, módulo nem etapa.

## Consequências negativas

- Todo ato depende do registro inteiro. Mudar o que é uma atividade mexe em quem lê a situação.
- Acompanhamento não tem dados próprios. Documento e atividade entram pelo processo, não por um armazenamento separado.

## Custos e riscos

- O registro cresce com as atividades. No volume do protótipo, o ato carrega o processo. Se as atividades forem muitas, a leitura delas continua neste repositório. Não vira outro estilo.
- Risco de partir o registro em bancos de vaga, de candidatura e de estágio e remontar a situação na aplicação. A consulta volta a juntar pedaços, e o repository deixa de ser o centro.

# Proposta arquitetural

## 1. Visão geral

O sistema de gerenciamento de estágios adota um **monólito modular com arquitetura hexagonal (portas e adaptadores)**, conforme o [ADR-01](adr/ADR-01.md). Vagas, candidaturas, homologação, documentos e atividades fazem parte do mesmo processo de estágio e precisam compartilhar seu estado. Por isso, no escopo do protótipo, a comunicação interna ocorrerá em uma única aplicação, por chamadas locais, sem separar os módulos em serviços de rede.

A divisão em módulos organiza as responsabilidades do negócio; as portas isolam o núcleo de detalhes de infraestrutura, como o armazenamento e o canal de notificação. A proposta se relaciona aos requisitos arquiteturalmente significativos descritos em [requisitos.md](requisitos.md):

- **ASR1 — evolução das regras:** centralizar documentos obrigatórios e responsáveis pelas aprovações em uma política de estágio;
- **ASR2 — substituição de integração:** utilizar uma porta de notificação independente do canal concreto;
- **ASR3 — proteção de dados:** aplicar o recorte de informações por papel em um ponto central da consulta de situação.

O objetivo é facilitar mudanças sem introduzir a complexidade operacional de múltiplos serviços independentes.

## 2. Organização e componentes

A arquitetura distingue a **entrada da aplicação**, o **núcleo de negócio** e os **adaptadores de infraestrutura**.

| Componente | Responsabilidade | Fronteira principal |
| --- | --- | --- |
| Aplicação / casos de uso | Receber operações, coordenar os módulos, verificar permissões e compor a resposta da consulta | Não executa SQL nem implementa canais de aviso diretamente |
| Vagas | Cadastrar vagas, registrar candidaturas e aceitar ou recusar candidaturas | Aplica as condições de vaga aberta, candidatura não duplicada e recusa com motivo |
| Estágio | Homologar candidatura aceita, vincular orientador e encerrar estágio | Controla a criação e a situação do estágio |
| Acompanhamento | Controlar documentos e registrar atividades | Exige estágio em andamento para novas atividades e respeita os estados dos documentos |
| Política de estágio | Definir documentos obrigatórios e quem pode aprovar cada etapa | É consultada pelos casos de uso, evitando regras duplicadas |
| Adaptador de persistência | Implementar a porta de repositório e conservar o processo entre execuções | Tecnologia concreta de banco não definida nos documentos atuais |
| Adaptador de notificação | Implementar a porta de aviso e comunicar decisões aos estudantes | Na primeira entrega, utiliza canal simulado |

Os quatro módulos **Vagas**, **Estágio**, **Acompanhamento** e **Política de estágio** compõem o núcleo definido no ADR-01. A camada de aplicação coordena operações e aplica o controle de acesso. Repositório e notificador são implementações externas às regras de negócio.

### Esquema conceitual

```text
Usuários / interface de entrada (a definir)
                    |
                    v
        Aplicação / casos de uso
        (orquestração e autorização)
                    |
                    v
   +-----------------------------------+
   |       Núcleo de negócio           |
   |                                   |
   |  Vagas            Estágio         |
   |  Acompanhamento   Política        |
   |                                   |
   |  Portas: Repositório / Notificação|
   +-----------------------------------+
                ^               ^
                | implementam   | implementam
       +--------+----+    +-----+-----------+
       | Adaptador de |    | Adaptador de    |
       | persistência |    | notificação     |
       +-------------+    +-----------------+
             |                   |
        Armazenamento       Canal simulado
```

As setas dos adaptadores representam **dependência de implementação em relação às portas definidas pelo núcleo**, não uma chamada de negócio do adaptador para o núcleo. Na execução, os casos de uso utilizam as portas para acessar essas implementações.

## 3. Dependências e interfaces

A regra fundamental é que **o núcleo não conhece as implementações concretas de persistência e notificação**. Os casos de uso dependem das interfaces necessárias e recebem as implementações escolhidas na composição da aplicação. Essa separação permite testar o comportamento do negócio sem iniciar um banco ou conectar-se a um serviço externo.

As duas portas previstas são:

- **Repositório do processo:** fornece operações de leitura e gravação do estado de vagas, candidaturas e estágio, inclusive orientador, documentos, atividades e encerramento. Cada operação consulta o estado atual, aplica a regra correspondente e persiste a alteração pelo repositório ([ADR-02](adr/ADR-02.md)).
- **Notificação de decisão:** recebe destinatário, tipo do evento, referência à candidatura ou ao estágio e motivo breve quando aplicável. Retorna sucesso ou informação de falha do canal ([ADR-03](adr/ADR-03.md)).

A **Política de estágio** é um componente do próprio núcleo, consultado pelos demais módulos para identificar documentos obrigatórios e responsáveis por aprovações. Ela não deve ser replicada em telas, consultas SQL ou casos de uso separados.

Os nomes de métodos, classes e assinaturas exatas dessas interfaces ainda dependerão da linguagem e da implementação do protótipo. Portanto, as descrições acima definem **contratos arquiteturais**, não uma API já implementada.

## 4. Comunicação e controle de acesso

### Comunicação interna

Os módulos comunicam-se por **chamadas locais** dentro do monólito, respeitando as interfaces e responsabilidades estabelecidas. Não há necessidade de REST, SOAP ou filas entre Vagas, Estágio e Acompanhamento. Essa decisão evita comunicação distribuída para operações que dependem do mesmo registro de processo.

A tecnologia de entrada (por exemplo, interface web ou API HTTP) **ainda não foi escolhida** nos documentos fornecidos. Independentemente dela, as solicitações devem passar pelos casos de uso da aplicação, em vez de acessar o repositório diretamente.

### Consulta da situação (RF07)

A consulta reúne a situação do processo — vaga, candidatura, homologação, orientador, documentos e atividades — e, **antes de entregar o resultado**, aplica o recorte correspondente ao papel do solicitante (RNF01 e ASR3). A verificação ocorre em um ponto central da aplicação, não em filtros independentes em cada tela.

Assim, o estudante consulta seu próprio processo; o orientador acessa os estágios sob sua orientação; a concedente acessa somente informações permitidas dos processos ligados às suas vagas; e a coordenação possui acesso compatível com suas atribuições. A aplicação não deve expor automaticamente a todos os atores o registro completo do repositório.

### Comunicação externa

A comunicação de avisos segue uma **porta de notificação**, inicialmente implementada por um adaptador simulado. O canal pode ser substituído futuramente por e-mail, REST ou SOAP sem alterar a regra de aceitação, homologação ou encerramento. Não se adota mensageria ou processamento distribuído para avisos nesta primeira versão ([ADR-03](adr/ADR-03.md)).

## 5. Persistência

O [ADR-02](adr/ADR-02.md) define o estilo **Repository** para manter o estado do processo de estágio. A aplicação usa o repositório para recuperar e gravar o processo, em vez de tratar cada ato como uma etapa independente que passa sua saída à próxima.

O registro contempla a vaga e suas candidaturas; após a homologação, também contempla o estágio, seu orientador, seus documentos, suas atividades e o encerramento. Documentos são itens identificados por **tipo e estado** (pendente, entregue ou recusado), o que permite acrescentar um novo documento exigido pela política sem criar um fluxo de armazenamento separado.

A persistência deve atender ao RNF02: dados de vaga, candidatura, estágio, documento e atividade sobrevivem ao reinício da aplicação. O tipo de banco de dados e o esquema físico **não foram definidos pelos ADRs**; essa escolha deve ser compatível com a porta de repositório e com o protótipo.

Centralizar o processo simplifica a consulta de situação, mas implica que o registro pode crescer com o histórico de atividades. Essa limitação já está reconhecida no ADR-02 e deve ser reavaliada caso o volume de dados cresça significativamente.

## 6. Integração de notificações e tratamento de falhas

O RF09 prevê avisos quando a candidatura é aceita ou recusada, quando o estágio é homologado, quando um documento é recusado e quando o estágio é encerrado. A saída é tratada pelo adaptador da **porta de notificação**, conforme o ADR-03.

A sequência definida é:

1. O caso de uso valida a operação e registra a decisão no repositório.
2. **Depois da persistência bem-sucedida**, solicita o envio do aviso pela porta de notificação.
3. Se o canal falhar, a decisão não é desfeita e o aviso é indicado como **pendente** (RNF03).

O adaptador simulado permite demonstrar sucesso e falha sem integração institucional real (RNF04). A porta não decide quem foi aceito, não aprova documentos e não desfaz homologações: apenas comunica uma decisão já registrada.

**Limitação reconhecida:** o ADR-03 não promete entrega garantida. Se a aplicação parar entre persistir a decisão e tentar enviar o aviso, poderá perder essa tentativa. Um mecanismo como *Transactional Outbox* é uma evolução possível se a garantia de entrega se tornar requisito. A forma concreta de registrar e consultar avisos pendentes ainda precisa ser detalhada na implementação, sem contrariar o RNF03.

## 7. Exemplo de interação: homologação do estágio

O caso de uso de homologação (RF04) mostra as responsabilidades em funcionamento:

1. A coordenação solicita a homologação de uma candidatura e indica o orientador.
2. A aplicação verifica se o solicitante tem permissão para executar a operação.
3. O caso de uso recupera o processo pelo repositório.
4. O módulo **Estágio** verifica que a candidatura foi aceita; consulta a **Política de estágio** para as regras de aprovação pertinentes.
5. O estágio é criado, o orientador é vinculado e o estado atualizado é persistido.
6. A aplicação solicita o aviso de homologação pela porta de notificação.
7. Se o aviso falhar, a homologação continua válida e o aviso é tratado como pendente.

Se a candidatura não tiver sido aceita, o processo não poderá ser homologado (RF04). Como exemplo de consulta, o RF07 recupera a situação já persistida e retorna somente os campos autorizados ao usuário.

Esse fluxo serve como referência para os diagramas e para o recorte implementado no protótipo; **não significa que o código já exista**.
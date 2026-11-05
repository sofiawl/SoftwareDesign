# Gerenciamento de estágios 

Sistema para cadastrar vagas de estágio, receber candidaturas, acompanhar aprovações, registrar orientadores e controlar documentos e atividades do
estágio. 

**Como este sistema deve ser organizado para atender aos requisitos atuais e permitir sua evolução sem gerar dependências desnecessárias?**

## O que não pode faltar na entrega
- [ ] documentações do projeto
- [ ] diagramas
- [ ] registros e decisões arquiteturais
- [ ] coódigo-fonte
- [ ] testes
- [ ] protótipo executável

## Documentação
### Descrição do problema e requisitos
- apresentar brevemente o contexto do sistema
- identificar os principais atores
- definir entre 6 e 10 requisitos funcionais
- identificar restrições relevantes
- selecionar e descrever 3 requisitos arquiteturalmente significativos (ASRs)
- justificar por que esses ASRs influenciam decisões arquiteturais

### Modelo de domínio e responsabilidades
- principais classes/conceitos do domínio
- responsabilidades de cada classe
- justificativas relacionadas a GRASP, quando necessário
- análise de coesão e acoplamento
- aplicação de princípios SOLID quando pertinente

### Modelagem UML
- Diagrama de Classes
- Diagrama de Sequência
- Diagrama de Comunicação
- Diagrama de Componentes ou Pacotes

### Proposta arquitetural
- principais componentes ou módulos
- responsabilidade de cada componente
- dependências entre eles
- interfaces relevantes
- mecanismos de comunicação
- persistência
- integrações externas
- decisões de comunicação
- Documentação de API, quando necessário


### Alternativas e trade-offs
- pelo menos duas alternativas arquiteturais além da solução escolhida
- comparação deve considerar: modificabilidade, desempenho, disponibilidade, testabilidade, complexidade, implantação, escalabilidade, custo de desenvolvimento e operação

### ADRs
- pelo menos 3 ADRs
- Cada um com contexto, problema ou forças envolvidas, alternativas consideradas, decisão, consequências positivas, consequências negativas, custos ou riscos

## Implementação
### Protótipo
- um caso de uso que modifica o estado do sistema
- uma consulta
- um fluxo alternativo ou erro relevante
- persistência dos dados
- pelo menos uma dependência externa simulada ou real

### Dependência externa
- pelo menos uma integração que possa ser substituída

### Análise de evolução
- Se uma das principais tecnologias ou integrações utilizadas precisasse ser substituída, quais partes do sistema seriam afetadas?
- Pelo menos duas mudanças
- Explicar: quais elementos seriam afetados, quais permaneceriam inalterados, que decisões arquiteturais ajudariam ou dificultariam a mudança


## Separação de tarefas

### Sofia
- Descrição do problema e requisitos
- ADRs

### pessoa 02
- Modelo de domínio e responsabilidades
- Análise de evolução

### pessoa 03
- Modelagem UML
- Alternativas e trade-offs

### pessoa 04
- Proposta arquitetural
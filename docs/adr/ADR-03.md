# ADR-03: Aviso de decisão atrás de uma interface

Status: aceita

## Contexto

O estudante precisa ser avisado quando a concedente decide a candidatura, quando a coordenação homologa o estágio, quando recusa um documento e quando encerra o estágio. O enunciado pede ao menos uma dependência externa que dê para substituir, e a análise de evolução pergunta o que quebra se essa integração for trocada. No protótipo não há SMTP institucional nem API acadêmica disponível. O [ADR-01](ADR-01.md) reserva essa saída à camada de infraestrutura. Este ADR fixa o contrato e o que acontece quando o aviso falha. É a resposta direta ao [ASR2](../requisitos.md#asr2).

## Problema e forças

- O estudante é avisado em cinco momentos: candidatura aceita ou recusada, estágio homologado, documento recusado, estágio encerrado.
- Perder a homologação porque o aviso falhou é pior do que o estudante ficar sem mensagem. A decisão já registrada permanece, e o aviso fica pendente.
- Nesta entrega não existe serviço da instituição. O aviso tem de funcionar mesmo assim, e depois tem de poder ser trocado sem reescrever a decisão.

## Alternativas consideradas

**O caso de uso chama o canal (REST ou SOAP).** Decidir a candidatura, homologar, recusar documento e encerrar conhecem o endereço e o formato da instituição. O protótipo não tem esse serviço, então o simulado entra como um desvio dentro desses quatro atos. Quando o canal passar a ser o e-mail da instituição, os quatro são editados de novo. O registro da decisão fica amarrado ao transporte.

**Fila (pub/sub).** O aviso é publicado e outro processo entrega. Isso segura a mensagem se o processo cair no meio do envio. Aqui o que não pode se perder é a homologação, e ela já está gravada. A fila pode avisar o estudante de uma decisão que a gravação ainda desfez, ou avisar duas vezes a mesma homologação. O fluxo não precisa disso: se o envio falha, o aviso fica pendente.

**Interface de aviso, chamada depois de gravar.** O caso de uso registra a decisão e então pede o aviso. Não sabe se o canal é simulado, e-mail, REST ou SOAP. A implementação desta entrega guarda o aviso e pode falhar de propósito, para o aviso pendente aparecer na avaliação. Trocar o canal troca a implementação.

## Decisão

Criar uma interface única de aviso, `Notificador`, definida na camada de aplicação e implementada na infraestrutura:

- entrada: destinatário, tipo do evento (candidatura aceita, candidatura recusada, estágio homologado, documento recusado, estágio encerrado), identificador de referência (candidatura ou estágio) e texto curto do motivo quando houver recusa ou encerramento;
- saída: sucesso, ou falha com o motivo do canal.

Ordem no caso de uso: persistir a decisão, depois notificar. Se o `Notificador` falhar, a decisão permanece, o caso de uso grava um `AvisoPendente` pelo `RepositorioProcesso` e devolve aviso pendente. Essa gravação é uma escrita explícita do caso de uso: o aviso pendente sobrevive ao reinício ([RNF02](../requisitos.md)) e fica disponível para nova tentativa manual. Não há escrita escondida na implementação do notificador, nem para guardar o aviso nem para "desfazer" homologação.

A implementação da primeira entrega é simulada: guarda os avisos emitidos e pode ser instruído a falhar, para o fluxo alternativo de aviso pendente ser demonstrável. E-mail ou API da instituição entram como outra implementação, sem mudar a interface.

A interface não escolhe quem ganhou a vaga e não valida documento. Ela só comunica uma decisão que o domínio já gravou.

## Consequências positivas

- Substituir o simulado por e-mail altera a implementação na infraestrutura e a composição do processo. Os casos de uso de candidatura, homologação, documento e encerramento ficam.
- O fluxo de erro do enunciado existe: decisão gravada, aviso pendente, sem estado pela metade.
- Teste do caso de uso usa um dublê que conta chamadas e simula falha. Não abre socket.

## Consequências negativas

- O simulado não exercita timeout real, credencial nem duplicidade de envio. A equipe pode achar que a interface está pronta para produção porque o log mostrou a mensagem.
- Entre gravar e avisar, uma queda do processo perde o aviso e não a decisão. O estudante fica sem mensagem até uma nova tentativa manual. É o custo de não adotar outbox.
- Um contrato pobre demais (só uma string livre) espalha formato de frase pelos casos de uso. Por isso o tipo do evento é enumerado, não texto inventado em cada chamada.

## Custos e riscos

- Custo: a interface, a implementação simulada e um teste de falha por caso de uso que avisa.
- Risco de efeito escondido: chamar o `Notificador` antes de persistir. Se o aviso sair e a transação desfizer, o estudante recebe uma decisão que não existe. A ordem (gravar, depois avisar) é parte da decisão, não detalhe de implementação.
- Risco de segunda interface paralela ("já que temos e-mail, chama direto no encerramento"). Qualquer aviso novo desta família usa a mesma interface.
- Se o aviso passar a ser requisito legal com garantia de entrega, este ADR deve ser substituído por um que adote outbox. A interface pode permanecer; muda a implementação e a garantia, não o caso de uso.

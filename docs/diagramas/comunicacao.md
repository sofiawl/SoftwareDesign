# Diagrama de comunicação - Consultar situação (RF07, RNF01, ASR3)

Mensagens numeradas na ordem de execução. O retorno aparece na própria mensagem (`resultado := operação`).

```mermaid
flowchart LR
    Ator(["Solicitante<br/>(estudante, concedente,<br/>orientador ou coordenação)"])
    Ctrl["ctrl : SituacaoController<br/>(apresentação)"]
    View["view : TelaSituacao<br/>(apresentação)"]
    UC["cs : ConsultarSituacao<br/>(aplicação)"]
    Leit["leitura : LeituraSituacao<br/>(implementada por RepositorioPersistente)"]
    Rec["recorte : RecortePorPapel<br/>(domínio)"]

    Ator -- "1: consultar(candidaturaId)" --> Ctrl
    Ctrl -- "1.1: visivel := executar(solicitante, candidaturaId)" --> UC
    UC -- "1.1.1: situacao := carregar(candidaturaId)" --> Leit
    UC -- "1.1.2: visivel := recortar(situacao, solicitante)" --> Rec
    Ctrl -- "1.2: exibir(visivel)" --> View
```

O `SituacaoController` monta o `Solicitante` (id e papel) a partir da sessão e chama o caso de uso. O recorte por papel só acontece em `RecortePorPapel`, depois que `LeituraSituacao` junta vaga, candidatura, estágio, documentos e atividades. O resultado é uma `SituacaoVisivel` ou `AcessoNegado`.

Nem o Controller nem a View filtram dado: a tela exibe exatamente o que recebeu. Nenhuma tela lê o banco por conta própria.

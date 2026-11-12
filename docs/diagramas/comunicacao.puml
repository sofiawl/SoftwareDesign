Mensagens numeradas na ordem de execução.
 
```mermaid
flowchart LR
    Ator(["Solicitante<br/>(estudante, concedente,<br/>orientador ou coordenação)"])
    UC["cs : ConsultarSituacao"]
    Leit["leitura : LeituraSituacao<br/>(RepositorioPersistente)"]
    Rec["recorte : RecortePorPapel"]
 
    Ator -- "1: executar(solicitante, candidaturaId)" --> UC
    UC -- "1.1: carregar(candidaturaId)<br/>1.2: situacao : SituacaoProcesso" --> Leit
    UC -- "1.3: recortar(situacao, solicitante)<br/>1.4: SituacaoVisivel ou AcessoNegado" --> Rec
```
 
O recorte por papel só acontece em `RecortePorPapel`, depois que `LeituraSituacao` junta vaga, candidatura, estágio, documentos e atividades. Nenhuma tela lê o banco por conta própria.

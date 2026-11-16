CREATE TABLE IF NOT EXISTS usuario (
    id     TEXT PRIMARY KEY,
    nome   TEXT NOT NULL,
    email  TEXT NOT NULL,
    papel  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vaga (
    id                    TEXT PRIMARY KEY,
    concedente_id         TEXT NOT NULL REFERENCES usuario(id),
    area                  TEXT NOT NULL,
    carga_horaria_semanal INTEGER NOT NULL,
    periodo               TEXT NOT NULL,
    pre_requisitos        TEXT NOT NULL,
    estado                TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS candidatura (
    id            TEXT PRIMARY KEY,
    vaga_id       TEXT NOT NULL REFERENCES vaga(id),
    estudante_id  TEXT NOT NULL REFERENCES usuario(id),
    estado        TEXT NOT NULL,
    motivo_recusa TEXT,
    UNIQUE (vaga_id, estudante_id)
);

CREATE TABLE IF NOT EXISTS estagio (
    id                  TEXT PRIMARY KEY,
    candidatura_id      TEXT NOT NULL UNIQUE REFERENCES candidatura(id),
    orientador_id       TEXT NOT NULL REFERENCES usuario(id),
    estado              TEXT NOT NULL,
    motivo_encerramento TEXT
);

CREATE TABLE IF NOT EXISTS documento (
    estagio_id    TEXT NOT NULL REFERENCES estagio(id),
    tipo          TEXT NOT NULL,
    estado        TEXT NOT NULL,
    motivo_recusa TEXT,
    PRIMARY KEY (estagio_id, tipo)
);

CREATE TABLE IF NOT EXISTS atividade (
    id            TEXT PRIMARY KEY,
    estagio_id    TEXT NOT NULL REFERENCES estagio(id),
    data          TEXT NOT NULL,
    descricao     TEXT NOT NULL,
    carga_horaria INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS aviso_pendente (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_evento     TEXT NOT NULL,
    referencia_id   TEXT NOT NULL,
    destinatario_id TEXT NOT NULL,
    motivo          TEXT,
    motivo_falha    TEXT NOT NULL,
    criado_em       TEXT NOT NULL
);

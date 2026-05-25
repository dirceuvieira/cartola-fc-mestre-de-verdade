-- DB schema for Mestre de Verdade (SQLite compatible)

-- Atletas
CREATE TABLE IF NOT EXISTS atletas (
  id INTEGER PRIMARY KEY,
  nome TEXT NOT NULL,
  apelido TEXT,
  clube_id INTEGER,
  posicao_id INTEGER,
  foto_url TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

-- Clubes
CREATE TABLE IF NOT EXISTS clubes (
  id INTEGER PRIMARY KEY,
  nome TEXT NOT NULL,
  abreviacao TEXT,
  escudo_url TEXT
);

-- Preços por rodada
CREATE TABLE IF NOT EXISTS precos (
  atleta_id INTEGER NOT NULL,
  rodada INTEGER NOT NULL,
  preco REAL,
  variacao REAL,
  PRIMARY KEY (atleta_id, rodada),
  FOREIGN KEY (atleta_id) REFERENCES atletas(id)
);

-- Pontuações por rodada
CREATE TABLE IF NOT EXISTS pontuacoes (
  atleta_id INTEGER NOT NULL,
  rodada INTEGER NOT NULL,
  pontuacao REAL,
  jogou INTEGER DEFAULT 0,
  PRIMARY KEY (atleta_id, rodada),
  FOREIGN KEY (atleta_id) REFERENCES atletas(id)
);

-- Scouts por rodada
CREATE TABLE IF NOT EXISTS scouts (
  atleta_id INTEGER NOT NULL,
  rodada INTEGER NOT NULL,
  gols INTEGER DEFAULT 0,
  assistencias INTEGER DEFAULT 0,
  desarmes INTEGER DEFAULT 0,
  defesas_dificeis INTEGER DEFAULT 0,
  gols_sofridos INTEGER DEFAULT 0,
  cartao_amarelo INTEGER DEFAULT 0,
  cartao_vermelho INTEGER DEFAULT 0,
  falta_cometida INTEGER DEFAULT 0,
  finalizacao_trave INTEGER DEFAULT 0,
  PRIMARY KEY (atleta_id, rodada),
  FOREIGN KEY (atleta_id) REFERENCES atletas(id)
);

-- Partidas
CREATE TABLE IF NOT EXISTS partidas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  rodada INTEGER NOT NULL,
  clube_casa_id INTEGER,
  clube_visitante_id INTEGER,
  placar_casa INTEGER,
  placar_visitante INTEGER,
  data TEXT
);

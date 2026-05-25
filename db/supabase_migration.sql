-- Supabase / PostgreSQL migration SQL for "Mestre de Verdade" collector
-- Creates tables, indices and provides example upsert statements and RLS notes

-- Enable useful extensions (optional)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Atletas
CREATE TABLE IF NOT EXISTS atletas (
  id BIGINT PRIMARY KEY,
  nome TEXT NOT NULL,
  apelido TEXT,
  clube_id BIGINT,
  posicao_id INT,
  foto_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_atletas_clube_id ON atletas(clube_id);
CREATE INDEX IF NOT EXISTS idx_atletas_posicao_id ON atletas(posicao_id);

-- Clubes
CREATE TABLE IF NOT EXISTS clubes (
  id BIGINT PRIMARY KEY,
  nome TEXT NOT NULL,
  abreviacao TEXT,
  escudo_url TEXT
);

-- Precos por rodada
CREATE TABLE IF NOT EXISTS precos (
  atleta_id BIGINT NOT NULL,
  rodada INT NOT NULL,
  preco NUMERIC(10,2),
  variacao NUMERIC(10,2),
  PRIMARY KEY (atleta_id, rodada),
  FOREIGN KEY (atleta_id) REFERENCES atletas(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_precos_rodada ON precos(rodada);
CREATE INDEX IF NOT EXISTS idx_precos_atleta ON precos(atleta_id);

-- Pontuações por rodada
CREATE TABLE IF NOT EXISTS pontuacoes (
  atleta_id BIGINT NOT NULL,
  rodada INT NOT NULL,
  pontuacao NUMERIC(10,2),
  jogou BOOLEAN DEFAULT FALSE,
  PRIMARY KEY (atleta_id, rodada),
  FOREIGN KEY (atleta_id) REFERENCES atletas(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_pontuacoes_rodada ON pontuacoes(rodada);
CREATE INDEX IF NOT EXISTS idx_pontuacoes_atleta ON pontuacoes(atleta_id);

-- Scouts por rodada
CREATE TABLE IF NOT EXISTS scouts (
  atleta_id BIGINT NOT NULL,
  rodada INT NOT NULL,
  gols INT DEFAULT 0,
  assistencias INT DEFAULT 0,
  desarmes INT DEFAULT 0,
  defesas_dificeis INT DEFAULT 0,
  gols_sofridos INT DEFAULT 0,
  cartao_amarelo INT DEFAULT 0,
  cartao_vermelho INT DEFAULT 0,
  falta_cometida INT DEFAULT 0,
  finalizacao_trave INT DEFAULT 0,
  PRIMARY KEY (atleta_id, rodada),
  FOREIGN KEY (atleta_id) REFERENCES atletas(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_scouts_rodada ON scouts(rodada);

-- Partidas
CREATE TABLE IF NOT EXISTS partidas (
  id BIGSERIAL PRIMARY KEY,
  rodada INT NOT NULL,
  clube_casa_id BIGINT REFERENCES clubes(id),
  clube_visitante_id BIGINT REFERENCES clubes(id),
  placar_casa INT,
  placar_visitante INT,
  data TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_partidas_rodada ON partidas(rodada);

-- Example upsert statements (use these patterns from the collector via SQL exec or client libraries)
-- Upsert atleta (single)
-- INSERT INTO atletas (id, nome, apelido, clube_id, posicao_id, foto_url)
-- VALUES (12345, 'Fulano', 'Fulano', 12, 3, 'https://...')
-- ON CONFLICT (id) DO UPDATE SET
--   nome = EXCLUDED.nome,
--   apelido = EXCLUDED.apelido,
--   clube_id = EXCLUDED.clube_id,
--   posicao_id = EXCLUDED.posicao_id,
--   foto_url = EXCLUDED.foto_url;

-- Upsert precos in batch (example using INSERT ... ON CONFLICT)
-- INSERT INTO precos (atleta_id, rodada, preco, variacao) VALUES
--   (12345, 12, 12.5, 0.5),
--   (23456, 12, 28.75, -0.25)
-- ON CONFLICT (atleta_id, rodada) DO UPDATE SET
--   preco = EXCLUDED.preco,
--   variacao = EXCLUDED.variacao;

-- Upsert pontuacoes similarly:
-- INSERT INTO pontuacoes (atleta_id, rodada, pontuacao, jogou) VALUES (...)
-- ON CONFLICT (atleta_id, rodada) DO UPDATE SET pontuacao = EXCLUDED.pontuacao, jogou = EXCLUDED.jogou;

-- Recommended indexes for common queries
-- - buscar histórico de um atleta: idx_precos_atleta, idx_pontuacoes_atleta
-- - rankings por rodada: idx_precos_rodada, idx_pontuacoes_rodada

-- Considerations for Supabase / RLS
-- - For initial prototype, RLS can be disabled. When enabling RLS, create policies allowing service-role keys to write.
-- Example policy (for service role use only):
-- ALTER TABLE precos ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "service_write" ON precos FOR INSERT USING (auth.role() = 'service_role');
-- NOTE: Supabase service_role key bypasses RLS; prefer using service_role for backend writes and anon for client reads.

-- Data types: NUMERIC is used for prices and scores to avoid floating point issues.
-- Timestamps use TIMESTAMPTZ for clarity across timezones.

-- Optional: create materialized views for aggregated queries (top valorizados por rodada)
-- CREATE MATERIALIZED VIEW mv_top_valorizados AS
-- SELECT atleta_id, rodada, preco, variacao FROM precos WHERE rodada = (SELECT MAX(rodada) FROM precos) ORDER BY variacao DESC LIMIT 100;

-- End of migration

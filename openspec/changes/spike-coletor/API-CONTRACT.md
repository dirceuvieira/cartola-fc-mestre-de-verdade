API Contract — Cartola FC (Spike)

Entities and minimal required fields

1. Atleta (from /atletas/mercado)
- atleta_id: int (PK)
- nome: string
- apelido: string (optional)
- clube_id: int
- posicao_id: int
- preco: numeric
- status: enum [disponivel, duvida, suspenso, contundido]
- foto_url: string (optional)

2. Preco (per rodada)
- atleta_id: int (FK)
- rodada: int (PK composite)
- preco: numeric
- variacao: numeric (optional)

3. Pontuacao
- atleta_id: int (FK)
- rodada: int (PK composite)
- pontuacao: numeric
- jogou: bool

4. Scouts
- atleta_id: int (FK)
- rodada: int (PK composite)
- gols, assistencias, desarmes, defesas_dificeis, etc (ints)

5. Partida
- id: int
- rodada: int
- clube_casa_id, clube_visitante_id: int
- placar_casa, placar_visitante: int (optional until after the match)
- data: datetime

Idempotency and upsert rules
- Upsert on (atleta_id) for atletas
- Upsert on (atleta_id, rodada) for precos, pontuacoes, scouts

Sanity checks
- Preco >= 0
- Pontuacao >= 0 (or allow negative? discuss — Cartola can have negative scores)
- String lengths reasonable (nome < 200)

Error handling
- On 429: backoff exponential, respect Retry-After header when present
- On 5xx: retry with capped backoff; log and alert if persistent

Versioning
- Snapshot responses to samples/ for audit


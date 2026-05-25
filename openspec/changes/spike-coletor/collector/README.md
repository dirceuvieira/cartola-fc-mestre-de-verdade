Collector PoC — Pseudocódigo e instruções

Objetivo

Documento descreve o fluxo do coletor single-run (pseudocódigo) e instruções para implementação segura, idempotente e testável.

Fluxo (pseudocódigo)

1. Setup
   - Carregar variáveis: CARTOLA_BASE_URL, SUPABASE_URL, SUPABASE_KEY
   - Inicializar cliente HTTP com timeouts e retries básicos
   - Inicializar client Supabase/Postgres

2. Determinar rodada atual
   - GET ${CARTOLA_BASE_URL}/mercado/status
   - rodada = response.rodada_atual

3. Coletar atletas e preços
   - GET ${CARTOLA_BASE_URL}/atletas/mercado
   - Para cada atleta:
     - Mapear campos para tabela atletas e precos
     - Upsert atleta (id)
     - Upsert preco por (atleta_id, rodada)

4. Coletar pontuações pós-rodada (se disponível)
   - GET ${CARTOLA_BASE_URL}/atletas/pontuados?rodada={rodada}
   - Upsert pontuacoes por (atleta_id, rodada)
   - Upsert scouts por (atleta_id, rodada)

5. Observability e logs
   - Logar duração por endpoint, status_code, quantidade de registros
   - Em caso de erro 429/5xx, aplicar backoff e retry

Idempotência
- Usar upsert com chave primária composta onde aplicável (atleta_id, rodada)
- Operações devem ser transacionais por entidade quando suportado

Teste manual
- Executar single_run.py três vezes e verificar ausência de duplicação

Runbook resumido
- Executar coletor: `python collector/single_run.py --env .env.dev`
- Checar logs em collector/logs/*.log

Observações
- Pseudocódigo: não implementar chamadas reais neste artefato (PoC apenas)

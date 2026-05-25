# Tasks — Spike: Coletor & Contratos da API

Objetivo: validar o contrato da API do Cartola e prover um coletor idempotente mínimo que popula o Supabase.

## Ambiente
- Criar projeto: branch `spike/coletor`
- Variáveis: CARTOLA_BASE_URL, SUPABASE_URL, SUPABASE_KEY, LOG_LEVEL

## Checklist do Spike (MVP)
- [x] 1. Chamar e registrar respostas de cada rota listada em `projeto_inicial.md`
  - Ex.: /mercado/status, /atletas/mercado, /atletas/pontuados, /partidas/{rodada}, /clubes, /posicoes
  - Artefato: `samples/<rota>-responses.json`
- [ ] 2. Medir latência e registrar erros (10 chamadas por rota)
  - Artefato: `spike/latency-report.md`
- [ ] 3. Documentar contrato por entidade (API-CONTRACT.md)
  - Campos obrigatórios, tipos, exemplos
- [x] 4. Implementar script coletor single-run (Python)
  - Identifica rodada via `/mercado/status`
  - Grava atletas, preços e pontuações no Supabase (upsert por PK)
  - Artefato: `collector/single_run.py`
- [ ] 5. Testar idempotência (rodar 3x sem duplicação)
- [x] 6. Suíte de testes de contrato (pytest)
  - Valida campos obrigatórios, enums, sanity checks
- [ ] 7. Policies de retry/backoff e circuit-breaker (documentar)
- [ ] 8. Observability mínima: logs estruturados + metric last_success_timestamp

## Tarefas operacionais
- [ ] Criar schema DB inicial (scripts SQL em `db/schema.sql`) — seguir `projeto_inicial.md`
- [ ] Provisionar Supabase de teste e configurar secrets
- [ ] Commit inicial do collector + README de execução

## Critérios de Aceitação (Spike)
- [ ] Todas as rotas respondem e foram documentadas (API-CONTRACT.md)
- [ ] Collector single-run grava dados no Supabase sem duplicações
- [ ] Testes de contrato passam localmente
- [ ] Relatório de latência e recomendação de cadence (ex: partials Xs / pós-rodada)

## Próximos passos pós-spike (opcional)
- [ ] Transformar collector em job cron + fila (RQ / Celery / Prefect)
- [ ] Adicionar FastAPI para agregações e parciais
- [ ] Adicionar cache Redis para parciais de alta frequência

---
Gerado automaticamente a partir do documento `projeto_inicial.md` — Spike inicial para implementação do coletor.

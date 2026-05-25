# Spike: Coletor & contratos API — Proposal

Objetivo

Validar o contrato da API Cartola, construir um coletor single-run idempotente que popula o Supabase e entregar documentação de contrato e runbook.

Escopo

- Coletar rotas essenciais: /mercado/status, /atletas/mercado, /atletas/pontuados, /partidas/{rodada}, /clubes, /posicoes
- Gerar samples JSON das respostas
- Implementar script coletor single-run (PoC)
- Criar testes de contrato (pytest skeleton) que validem campos e tipos

Entregáveis

- samples/ (exemplos JSON)
- collector/ (pseudocódigo e instruções)
- tests/ (test skeletons e mocks)
- tasks.md (já criado em openspec/analise_negocio)

Tempo estimado: 3–5 dias de spike


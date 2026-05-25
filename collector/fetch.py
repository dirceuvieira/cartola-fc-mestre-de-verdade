"""HTTP collector utilities for Cartola API.

Provides fetch functions that accept a configured requests.Session and return parsed JSON.
The run_collect function performs a full collect + upsert into the local SQLite DB (PoC).
"""
from typing import Any, Dict, List
import logging
import os

LOG = logging.getLogger("collector.fetch")


def fetch_mercado_status(session, base_url: str) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}/mercado/status"
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def fetch_atletas_mercado(session, base_url: str) -> List[Dict[str, Any]]:
    url = f"{base_url.rstrip('/')}/atletas/mercado"
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    return resp.json()


def fetch_atletas_pontuados(session, base_url: str, rodada: int) -> List[Dict[str, Any]]:
    url = f"{base_url.rstrip('/')}/atletas/pontuados?rodada={rodada}"
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    return resp.json()


# The run_collect function supports writing either to local SQLite (PoC) or Supabase via SupabaseWriter
def run_collect(db_path: str, base_url: str, session, supabase_writer=None):
    """Run a full collect. If supabase_writer is provided (SupabaseWriter), writes are sent to Supabase.
    Otherwise, writes go to local SQLite using single_run upsert helpers.
    """
    # import here to avoid circular import during test discovery
    from collector.single_run import create_connection, create_tables, upsert_atleta, upsert_preco, upsert_pontuacao

    # Prepare containers if using Supabase
    atletas_payload = []
    precos_payload = []
    pontuacoes_payload = []

    status = fetch_mercado_status(session, base_url)
    rodada = status.get('rodada_atual')
    LOG.info('Collecting for rodada %s', rodada)

    atletas = fetch_atletas_mercado(session, base_url)
    # atletas may be a dict with nested structure depending on API; prefer list
    if isinstance(atletas, dict) and 'atletas' in atletas:
        atletas_list = atletas['atletas']
    else:
        atletas_list = atletas

    for a in atletas_list:
        # normalize keys if needed
        atleta_id = a.get('atleta_id') or a.get('id')
        if atleta_id is None:
            LOG.warning('Skipping atleta without id: %s', a)
            continue

        if supabase_writer:
            # map to DB contract
            atleta_obj = {
                'id': atleta_id,
                'nome': a.get('nome'),
                'apelido': a.get('apelido'),
                'clube_id': a.get('clube_id'),
                'posicao_id': a.get('posicao_id'),
                'foto_url': a.get('foto_url') or a.get('foto')
            }
            atletas_payload.append(atleta_obj)
            preco = a.get('preco') or a.get('valor')
            if preco is not None and rodada is not None:
                precos_payload.append({
                    'atleta_id': atleta_id,
                    'rodada': int(rodada),
                    'preco': float(preco),
                    'variacao': a.get('variacao')
                })
        else:
            # local sqlite path
            conn = create_connection(db_path)
            create_tables(conn)
            upsert_atleta(conn, a)
            preco = a.get('preco') or a.get('valor')
            if preco is not None and rodada is not None:
                try:
                    upsert_preco(conn, atleta_id, int(rodada), float(preco))
                except Exception:
                    LOG.exception('Failed upsert_preco for %s', atleta_id)
            conn.close()

    # collect pontuados if rodada is available
    if rodada is not None:
        pontuados = fetch_atletas_pontuados(session, base_url, int(rodada))
        if isinstance(pontuados, dict) and 'atletas' in pontuados:
            pont_list = pontuados['atletas']
        else:
            pont_list = pontuados
        for p in pont_list:
            atleta_id = p.get('atleta_id') or p.get('id')
            rodada_p = p.get('rodada') or rodada
            if supabase_writer:
                pontuacoes_payload.append({
                    'atleta_id': atleta_id,
                    'rodada': int(rodada_p),
                    'pontuacao': float(p.get('pontuacao', 0)),
                    'jogou': bool(p.get('jogou', False))
                })
            else:
                conn = create_connection(db_path)
                create_tables(conn)
                try:
                    upsert_pontuacao(conn, atleta_id, int(rodada_p), float(p.get('pontuacao', 0)), bool(p.get('jogou', False)))
                except Exception:
                    LOG.exception('Failed upsert_pontuacao for %s', atleta_id)
                conn.close()

    # If using Supabase, flush payloads
    if supabase_writer:
        if atletas_payload:
            supabase_writer.upsert_atletas(atletas_payload)
        if precos_payload:
            supabase_writer.upsert_precos(precos_payload)
        if pontuacoes_payload:
            supabase_writer.upsert_pontuacoes(pontuacoes_payload)

    LOG.info('Collect finished')

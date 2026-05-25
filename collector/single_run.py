"""Collector PoC

- Supports ingesting sample JSON into local SQLite for testing
- Provides basic HTTP fetch helpers (not executed in tests)
"""
import os
import json
import sqlite3
import logging
import argparse
from typing import Any, Dict
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

LOG = logging.getLogger("collector")

CREATE_TABLES_SQL = """
-- tables are created by executing statements in db/schema.sql; replicated here for sqlite PoC
"""

def setup_http_session(retries: int = 3, backoff: float = 0.5) -> Session:
    s = Session()
    retry = Retry(total=retries, backoff_factor=backoff, status_forcelist=(429, 500, 502, 503, 504))
    adapter = HTTPAdapter(max_retries=retry)
    s.mount('https://', adapter)
    s.mount('http://', adapter)
    return s

def create_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables(conn: sqlite3.Connection):
    sql_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'schema.sql')
    sql_path = os.path.normpath(sql_path)
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()

def upsert_atleta(conn: sqlite3.Connection, atleta: Dict[str, Any]):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO atletas (id, nome, apelido, clube_id, posicao_id, foto_url, created_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
          nome=excluded.nome,
          apelido=excluded.apelido,
          clube_id=excluded.clube_id,
          posicao_id=excluded.posicao_id,
          foto_url=excluded.foto_url
        """,
        (
            atleta.get('atleta_id') or atleta.get('id'),
            atleta.get('nome'),
            atleta.get('apelido'),
            atleta.get('clube_id'),
            atleta.get('posicao_id'),
            atleta.get('foto_url') or atleta.get('foto')
        )
    )
    conn.commit()

def upsert_preco(conn: sqlite3.Connection, atleta_id: int, rodada: int, preco: float, variacao: float = None):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO precos (atleta_id, rodada, preco, variacao)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(atleta_id, rodada) DO UPDATE SET
          preco=excluded.preco,
          variacao=excluded.variacao
        """,
        (atleta_id, rodada, preco, variacao)
    )
    conn.commit()

def upsert_pontuacao(conn: sqlite3.Connection, atleta_id: int, rodada: int, pontuacao: float, jogou: bool):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO pontuacoes (atleta_id, rodada, pontuacao, jogou)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(atleta_id, rodada) DO UPDATE SET
          pontuacao=excluded.pontuacao,
          jogou=excluded.jogou
        """,
        (atleta_id, rodada, pontuacao, int(bool(jogou)))
    )
    conn.commit()

def ingest_atletas_from_sample(conn: sqlite3.Connection, sample_path: str, rodada: int = None):
    with open(sample_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for a in data:
        upsert_atleta(conn, a)
        if rodada is not None and ('preco' in a or 'valor' in a):
            preco = a.get('preco') or a.get('valor')
            try:
                upsert_preco(conn, a.get('atleta_id') or a.get('id'), rodada, float(preco))
            except Exception:
                LOG.exception('Failed to upsert preco for %s', a)

def ingest_pontuados_from_sample(conn: sqlite3.Connection, sample_path: str):
    with open(sample_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for p in data:
        atleta_id = p.get('atleta_id') or p.get('id')
        rodada = p.get('rodada')
        pontuacao = p.get('pontuacao')
        jogou = p.get('jogou')
        upsert_pontuacao(conn, atleta_id, rodada, pontuacao, jogou)
        # scouts are intentionally ignored in PoC DB writes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='data/coletor.db', help='SQLite DB path')
    parser.add_argument('--samples-dir', default=None, help='Optional samples directory to ingest')
    parser.add_argument('--ingest-samples', action='store_true', help='Run ingest from samples and exit')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    db_path = args.db
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = create_connection(db_path)
    create_tables(conn)

    if args.ingest_samples and args.samples_dir:
        # ingest known samples
        mercado = os.path.join(args.samples_dir, 'atletas-mercado-sample.json')
        pontuados = os.path.join(args.samples_dir, 'atletas-pontuados-sample.json')
        if os.path.exists(mercado):
            ingest_atletas_from_sample(conn, mercado, rodada=None)
        if os.path.exists(pontuados):
            ingest_pontuados_from_sample(conn, pontuados)
        LOG.info('Ingest completed from samples')

if __name__ == '__main__':
    main()

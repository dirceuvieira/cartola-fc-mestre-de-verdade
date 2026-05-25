import tempfile
import os
import sqlite3
from collector import single_run

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'openspec', 'changes', 'spike-coletor', 'samples')


def test_ingest_atletas_and_pontuados():
    with tempfile.TemporaryDirectory() as td:
        db_path = os.path.join(td, 'test.db')
        conn = single_run.create_connection(db_path)
        single_run.create_tables(conn)
        mercado_sample = os.path.join(SAMPLES_DIR, 'atletas-mercado-sample.json')
        pontuados_sample = os.path.join(SAMPLES_DIR, 'atletas-pontuados-sample.json')
        assert os.path.exists(mercado_sample)
        assert os.path.exists(pontuados_sample)
        single_run.ingest_atletas_from_sample(conn, mercado_sample, rodada=1)
        single_run.ingest_pontuados_from_sample(conn, pontuados_sample)
        cur = conn.cursor()
        cur.execute('SELECT COUNT(1) as c FROM atletas')
        c = cur.fetchone()[0]
        assert c >= 1
        cur.execute('SELECT COUNT(1) as c FROM pontuacoes')
        pc = cur.fetchone()[0]
        assert pc >= 1
        conn.close()

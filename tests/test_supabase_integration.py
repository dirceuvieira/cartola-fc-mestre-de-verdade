import tempfile
import os
from collector import fetch

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'openspec', 'changes', 'spike-coletor', 'samples')


class DummySupabaseWriter:
    def __init__(self):
        self.calls = {'atletas': [], 'precos': [], 'pontuacoes': []}

    def upsert_atletas(self, atletas):
        self.calls['atletas'].extend(atletas)

    def upsert_precos(self, precos):
        self.calls['precos'].extend(precos)

    def upsert_pontuacoes(self, ponts):
        self.calls['pontuacoes'].extend(ponts)


class DummySession:
    def get(self, url, timeout=10):
        import json
        if url.endswith('/mercado/status'):
            def _json(*a, **k):
                return __import__('json').load(open(os.path.join(SAMPLES_DIR, 'mercado-status-sample.json')))
            def _raise(*a, **k):
                return None
            return type('R', (), {'status_code':200, 'json': _json, 'raise_for_status': _raise})()
        if '/atletas/mercado' in url:
            def _json(*a, **k):
                return __import__('json').load(open(os.path.join(SAMPLES_DIR, 'atletas-mercado-sample.json')))
            def _raise(*a, **k):
                return None
            return type('R', (), {'status_code':200, 'json': _json, 'raise_for_status': _raise})()
        if '/atletas/pontuados' in url:
            def _json(*a, **k):
                return __import__('json').load(open(os.path.join(SAMPLES_DIR, 'atletas-pontuados-sample.json')))
            def _raise(*a, **k):
                return None
            return type('R', (), {'status_code':200, 'json': _json, 'raise_for_status': _raise})()
        def _json():
            return {}
        def _raise(*a, **k):
            return None
        return type('R', (), {'status_code':200, 'json': _json, 'raise_for_status': _raise})()


def test_run_collect_with_supabase_writer():
    with tempfile.TemporaryDirectory() as td:
        db_path = os.path.join(td, 'test.db')
        writer = DummySupabaseWriter()
        session = DummySession()
        fetch.run_collect(db_path, 'https://api.cartola.globo.com', session, supabase_writer=writer)
        # validate that writer received data
        assert len(writer.calls['atletas']) >= 1
        assert len(writer.calls['precos']) >= 0
        assert len(writer.calls['pontuacoes']) >= 0

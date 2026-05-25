import tempfile
import os
from collector import fetch
from collector.single_run import setup_http_session

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'openspec', 'changes', 'spike-coletor', 'samples')


class DummyResponse:
    def __init__(self, data):
        self._data = data
        self.status_code = 200

    def json(self):
        return self._data

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise Exception('HTTP error')


class DummySession:
    def __init__(self):
        self.calls = []

    def get(self, url, timeout=10):
        self.calls.append(url)
        if url.endswith('/mercado/status'):
            data = __import__('json').load(open(os.path.join(SAMPLES_DIR, 'mercado-status-sample.json')))
            return DummyResponse(data)
        if '/atletas/mercado' in url:
            data = __import__('json').load(open(os.path.join(SAMPLES_DIR, 'atletas-mercado-sample.json')))
            return DummyResponse(data)
        if '/atletas/pontuados' in url:
            data = __import__('json').load(open(os.path.join(SAMPLES_DIR, 'atletas-pontuados-sample.json')))
            return DummyResponse(data)
        return DummyResponse({})


def test_run_collect_with_dummy_session():
    with tempfile.TemporaryDirectory() as td:
        db_path = os.path.join(td, 'test.db')
        session = DummySession()
        fetch.run_collect(db_path, 'https://api.cartola.globo.com', session)
        # basic assertions: DB file created and calls were made
        assert os.path.exists(db_path)
        assert any('/mercado/status' in c for c in session.calls)
        assert any('/atletas/mercado' in c for c in session.calls)
        assert any('/atletas/pontuados' in c for c in session.calls)

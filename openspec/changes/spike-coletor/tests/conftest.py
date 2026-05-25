import pytest

# Fixtures placeholder for future mocks (http client, db client)

@pytest.fixture
def http_client_mock(monkeypatch):
    class DummyResponse:
        def __init__(self, data):
            self.data = data

        def json(self):
            return self.data

    def _load(name):
        with open('..\\samples\\' + name, 'r', encoding='utf-8') as f:
            return __import__('json').load(f)

    return {'load_sample': _load}

import json
import pytest

# Tests are skeletons using sample files in ../samples/

SAMPLES_DIR = "..\\samples\\"

def load_sample(name):
    with open(SAMPLES_DIR + name, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_mercado_status_contains_rodada_and_flag():
    data = load_sample('mercado-status-sample.json')
    assert 'rodada_atual' in data
    assert isinstance(data['rodada_atual'], int)
    assert 'mercado_aberto' in data
    assert isinstance(data['mercado_aberto'], bool)


def test_atletas_mercado_schema():
    data = load_sample('atletas-mercado-sample.json')
    assert isinstance(data, list)
    for a in data:
        assert 'atleta_id' in a and isinstance(a['atleta_id'], int)
        assert 'nome' in a and isinstance(a['nome'], str)
        assert 'preco' in a and (isinstance(a['preco'], float) or isinstance(a['preco'], int))
        assert 'status' in a and a['status'] in ['disponivel','duvida','suspenso','contundido']


def test_atletas_pontuados_schema():
    data = load_sample('atletas-pontuados-sample.json')
    assert isinstance(data, list)
    for p in data:
        assert 'atleta_id' in p and isinstance(p['atleta_id'], int)
        assert 'rodada' in p and isinstance(p['rodada'], int)
        assert 'pontuacao' in p
        assert 'jogou' in p and isinstance(p['jogou'], bool)


def test_pontuados_upsert_idempotent():
    # Skeleton: describe intent. Implement DB-upsert asserts when DB client is provided.
    sample = load_sample('atletas-pontuados-sample.json')
    # Simulate upsert: idempotency requirement — running twice yields same unique keys
    ids = set((p['atleta_id'], p['rodada']) for p in sample)
    assert len(ids) == len(sample)

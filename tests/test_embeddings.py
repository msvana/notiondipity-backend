from datetime import datetime

from base import client, db, TEST_HEADERS
from notiondipity_backend.resources import embeddings

assert client, db


def test_not_has_data(client):
    response = client.get('/has-data', headers=TEST_HEADERS)
    assert response.status_code == 200
    assert response.json['status'] == 'OK'
    assert response.json['hasData'] is False


def test_has_data(client, db):
    with db.connection() as conn:
        conn.execute('''
            INSERT INTO last_updates 
            VALUES ('22d195198acb6e3e9e88d3c88c7980aaeed170615269153719cbd16de455c921', '2023-06-19 10:38:23', 1)
        ''')
        conn.commit()
    response = client.get('/has-data', headers=TEST_HEADERS)
    assert response.status_code == 200
    assert response.json['status'] == 'OK'
    assert response.json['hasData'] is True


def test_refresh_too_soon(client, db):
    with db.connection() as conn:
        now = datetime.now()
        conn.execute('''
            INSERT INTO last_updates 
            VALUES ('22d195198acb6e3e9e88d3c88c7980aaeed170615269153719cbd16de455c921', %s, 1)
        ''', [now])
        conn.commit()
    response = client.get('/refresh-embeddings', headers=TEST_HEADERS)
    assert response.status_code == 425
    assert response.json['status'] == 'error'


def test_resfresh(client, db):
    response = client.get('/refresh-embeddings', headers=TEST_HEADERS)
    assert response.status_code == 200
    assert response.json['status'] == 'OK'
    with db.connection() as conn, conn.cursor() as cursor:
        all_embeddings = embeddings.get_all_embedding_records(
            cursor, '22d195198acb6e3e9e88d3c88c7980aaeed170615269153719cbd16de455c921')
    assert len(all_embeddings) == 7
    assert 'Welcome to Notion!' in all_embeddings[0].get_text('48c73c5c-0d53-4383-83e8-2ef1bfbebe4e')

from datetime import datetime

from base import aiotest, client, db, TEST_HEADERS
from notiondipity_backend.resources import embeddings

assert client, db


@aiotest
async def test_not_has_data(client):
    response = await client.get('/has-data', headers=TEST_HEADERS)
    assert response.status_code == 200
    json = await response.get_json()
    assert json['status'] == 'OK'
    assert json['hasData'] is False


@aiotest
async def test_has_data(client, db):
    with db.connection() as conn:
        conn.execute('''
            INSERT INTO last_updates 
            VALUES ('22d195198acb6e3e9e88d3c88c7980aaeed170615269153719cbd16de455c921', '2023-06-19 10:38:23', 1)
        ''')
        conn.commit()
    response = await client.get('/has-data', headers=TEST_HEADERS)
    assert response.status_code == 200
    json = await response.get_json()
    assert json['status'] == 'OK'
    assert json['hasData'] is True


@aiotest
async def test_refresh_too_soon(client, db):
    with db.connection() as conn:
        now = datetime.now()
        conn.execute('''
            INSERT INTO last_updates 
            VALUES ('22d195198acb6e3e9e88d3c88c7980aaeed170615269153719cbd16de455c921', %s, 1)
        ''', [now])
        conn.commit()
    response = await client.get('/refresh-embeddings', headers=TEST_HEADERS)
    assert response.status_code == 425
    json = await response.get_json()
    assert json['status'] == 'error'


@aiotest
async def test_resfresh(client, db):
    response = await client.get('/refresh-embeddings', headers=TEST_HEADERS)
    assert response.status_code == 200
    json = await response.get_json()
    assert json['status'] == 'OK'
    with db.connection() as conn, conn.cursor() as cursor:
        all_embeddings = embeddings.get_all_embedding_records(
            cursor, '22d195198acb6e3e9e88d3c88c7980aaeed170615269153719cbd16de455c921')
    assert len(all_embeddings) == 7
    assert 'Movie List' in all_embeddings[0].get_text('48c73c5c-0d53-4383-83e8-2ef1bfbebe4e')

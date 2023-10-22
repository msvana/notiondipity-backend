import asyncio
from datetime import datetime

from base import aiotest, client, db, TEST_HEADERS, TEST_USER_ID_HASH
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
        conn.execute("INSERT INTO last_updates VALUES (%s, '2023-06-19 10:38:23', 1)", (TEST_USER_ID_HASH,))
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
        conn.execute("INSERT INTO last_updates VALUES (%s, %s, 1)", (TEST_USER_ID_HASH, now))
        conn.commit()
    response = await client.get('/refresh-embeddings', headers=TEST_HEADERS)
    assert response.status_code == 425
    json = await response.get_json()
    assert json['status'] == 'error'


@aiotest
async def test_resfresh(client, db):
    response = await client.get('/refresh-embeddings', headers=TEST_HEADERS)
    await asyncio.sleep(15)
    assert response.status_code == 200
    json = await response.get_json()
    assert json['status'] == 'OK'
    with db.connection() as conn, conn.cursor() as cursor:
        all_embeddings = embeddings.get_all_embedding_records(cursor, TEST_USER_ID_HASH)
    assert len(all_embeddings) == 7
    for e in all_embeddings:
        assert e.parent_id is not None
        if e.page_id == '3b1f8efc-9d71-439b-9df7-e6c8697754bd':
            assert e.page_title == 'Movie List'
        if e.page_id == 'f6b59f53-b6c0-42af-8405-7ec94ef21954':
            assert 'Welcome to Notion! Here are the basics:' in e.get_text('48c73c5c-0d53-4383-83e8-2ef1bfbebe4e')

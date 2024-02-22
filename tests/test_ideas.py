from base import TEST_HEADERS, aiotest, client, db

assert client, db


@aiotest
async def test_ideas(client):
    page_contents = {
        'title': 'Ideas',
        'content': 'Sentiment analysis on social media',
        'pageId': '3e47e9f4-c534-4d74-96c9-790b36b1162e'
    }
    response = await client.post('/ideas/', headers=TEST_HEADERS, json=page_contents)
    assert response.status_code == 200
    json = await response.get_json()
    assert json['status'] == 'OK'
    assert len(json['ideas']) > 0
    for idea in json['ideas']:
        assert 'idea_id' in idea and idea['idea_id'] is not None
        assert 'title' in idea
        assert 'description' in idea
        assert idea['cached'] is False

    # Now the ideas should be cached
    response = await client.post('/ideas/', headers=TEST_HEADERS, json=page_contents)
    assert response.status_code == 200
    json_cached = await response.get_json()
    assert json_cached['status'] == 'OK'
    assert len(json_cached['ideas']) == len(json['ideas'])
    for idea in json_cached['ideas']:
        assert idea['cached'] is True


@aiotest
async def test_ideas_non_existing_page(client):
    """
    Should work too, but there will be no penalization of relatives
    """
    page_contents = {
        'title': 'Ideas',
        'content': 'Sentiment analysis on social media',
        'pageId': '3e47e9f4-c534-4d74-96c9-790b36b1161f'
    }
    await client.get('/refresh-embeddings', headers=TEST_HEADERS)
    response = await client.post('/ideas/', headers=TEST_HEADERS, json=page_contents)
    assert response.status_code == 200
    json = await response.get_json()
    assert json['status'] == 'OK'
    assert 'ideas' in json
    assert len(json['ideas']) > 0


@aiotest
async def test_ideas_long(client):
    with open('tests/data/long_text.md') as long_text_fd:
        content = long_text_fd.read()

    page_contents = {
        'title': 'Cvicenie',
        'content': content,
        'pageId': '3e47e9f4-c534-4d74-96c9-790b36b1162e'
    }
    response = await client.post('/ideas/', headers=TEST_HEADERS, json=page_contents)
    assert response.status_code == 200
    json = await response.get_json()
    assert json['status'] == 'OK'
    assert 'ideas' in json
    assert len(json['ideas']) > 0


@aiotest
async def test_ideas_refresh(client):
    with open('tests/data/long_text.md') as long_text_fd:
        content = long_text_fd.read()

    page_contents = {
        'title': 'Cvicenie',
        'content': content,
        'pageId': '3e47e9f4-c534-4d74-96c9-790b36b1162e',
        'refresh': False
    }
    await client.post('/ideas/', headers=TEST_HEADERS, json=page_contents)

    page_contents['refresh'] = True
    response = await client.post('/ideas/', headers=TEST_HEADERS, json=page_contents)
    json = await response.get_json()
    for idea in json['ideas']:
        assert idea['cached'] is False


@aiotest
async def test_ideas_save(client, db):
    page_contents = {
        'title': 'Cvicenie',
        'content': 'Sentiment analysis on social media',
        'pageId': '3e47e9f4-c534-4d74-96c9-790b36b1162e',
    }

    response = await client.post('/ideas/', headers=TEST_HEADERS, json=page_contents)
    json = await response.get_json()
    idea_id = json['ideas'][0]['idea_id']
    response = await client.get(f'/ideas/save/{idea_id}', headers=TEST_HEADERS)
    assert response.status_code == 200
    json = await response.get_json()
    assert json['status'] == 'OK'

    with db.connection() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT saved FROM ideas WHERE idea_id = %s", (idea_id,))
        result = cursor.fetchone()
        assert result[0] is True

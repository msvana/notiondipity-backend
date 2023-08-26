from base import client, db, TEST_HEADERS

assert client, db


def test_ideas(client):
    page_contents = {
        'title': 'Ideas',
        'content': 'Sentiment analysis on social media',
        'pageId': '3e47e9f4-c534-4d74-96c9-790b36b1162e'
    }
    client.get('/refresh-embeddings', headers=TEST_HEADERS)
    response = client.post('/ideas/', headers=TEST_HEADERS, json=page_contents)
    assert response.status_code == 200
    assert response.json['status'] == 'OK'
    assert 'ideas' in response.json
    assert len(response.json['ideas']) > 0


def test_ideas_non_existing_page(client):
    """
    Should work too, but there will be no penalization of relatives
    """
    page_contents = {
        'title': 'Ideas',
        'content': 'Sentiment analysis on social media',
        'pageId': '3e47e9f4-c534-4d74-96c9-790b36b1161f'
    }
    client.get('/refresh-embeddings', headers=TEST_HEADERS)
    response = client.post('/ideas/', headers=TEST_HEADERS, json=page_contents)
    assert response.status_code == 200
    assert response.json['status'] == 'OK'
    assert 'ideas' in response.json
    assert len(response.json['ideas']) > 0


def test_ideas_long(client):
    with open('tests/data/long_text.md') as long_text_fd:
        content = long_text_fd.read()
    page_contents = {
        'title': 'Cvicenie',
        'content': content,
        'pageId': '3e47e9f4-c534-4d74-96c9-790b36b1162e'
    }
    client.get('/refresh-embeddings', headers=TEST_HEADERS)
    response = client.post('/ideas/', headers=TEST_HEADERS, json=page_contents)
    assert response.status_code == 200
    assert response.json['status'] == 'OK'
    assert 'ideas' in response.json
    assert len(response.json['ideas']) > 0

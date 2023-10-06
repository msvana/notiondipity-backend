from base import aiotest, client, db, TEST_HEADERS

assert client, db


@aiotest
async def test_recommend(client):
    page_contents = {
        'title': 'Ideas',
        'content': 'Sentiment analysis on social media',
        'pageId': 'f4067fc5-80d2-496c-a306-8e8c6f53329a'
    }

    response = await client.post('/v2/recommend/', headers=TEST_HEADERS, json=page_contents)
    assert response.status_code == 200
    json = await response.get_json()
    assert 'recommendations' in json
    assert json['status'] == 'OK'
    assert len(json['recommendations']) == 2
    assert type(json['recommendations'][0]) == list
    assert len(json['recommendations'][0]) == 3


@aiotest
async def test_recommend_no_page_id(client):
    page_contents = {
        'title': 'Ideas',
        'content': 'Sentiment analysis on social media',
    }

    response = await client.post('/v2/recommend/', headers=TEST_HEADERS, json=page_contents)
    assert response.status_code == 200
    json = await response.get_json()
    assert 'recommendations' in json
    assert json['status'] == 'OK'
    assert len(json['recommendations']) == 3
    assert type(json['recommendations'][0]) == list
    assert len(json['recommendations'][0]) == 3

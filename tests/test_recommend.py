from base import client, db, TEST_HEADERS

assert client, db


def test_recommend_v2(client):
    page_contents = {
        'title': 'Ideas',
        'content': 'Sentiment analysis on social media',
        'pageId': 'f4067fc5-80d2-496c-a306-8e8c6f53329a'
    }

    response = client.post('/v2/recommend/', headers=TEST_HEADERS, json=page_contents)
    assert response.status_code == 200
    assert 'recommendations' in response.json
    assert response.json['status'] == 'OK'
    assert len(response.json['recommendations']) == 2
    assert type(response.json['recommendations'][0]) == list
    assert len(response.json['recommendations'][0]) == 3


def test_recommend_v2_no_page_id(client):
    page_contents = {
        'title': 'Ideas',
        'content': 'Sentiment analysis on social media',
    }

    response = client.post('/v2/recommend/', headers=TEST_HEADERS, json=page_contents)
    assert response.status_code == 200
    assert 'recommendations' in response.json
    assert response.json['status'] == 'OK'
    assert len(response.json['recommendations']) == 3
    assert type(response.json['recommendations'][0]) == list
    assert len(response.json['recommendations'][0]) == 3


def test_recommend_v1(client):
    page_contents = {
        'title': 'Ideas',
        'content': 'Sentiment analysis on social media'
    }

    response = client.post('/v1/recommend/9d57534dc9d043ba9660a434222078d8', headers=TEST_HEADERS, json=page_contents)

    assert response.status_code == 200
    assert 'currentPage' in response.json
    assert response.json['currentPage']['id'] == '9d57534dc9d043ba9660a434222078d8'
    assert response.json['currentPage']['title'] == 'Ideas'
    assert 'recommendations' in response.json
    assert len(response.json['recommendations']) == 3
    assert type(response.json['recommendations'][0]) == list
    assert len(response.json['recommendations'][0]) == 3

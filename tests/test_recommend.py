from base import client, TEST_HEADERS

assert client


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
    assert type(response.json['recommendations']) == list
    assert type(response.json['recommendations'][0]) == list
    assert len(response.json['recommendations'][0]) == 3

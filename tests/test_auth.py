from base import client, TEST_TOKEN

assert client


def test_no_token(client):
    response = client.get('/has-data')
    assert response.status_code == 401
    assert response.text == 'No authorization header present'


def test_no_bearer(client):
    response = client.get('/has-data', headers={'Authorization': 'Something'})
    assert response.status_code == 401
    assert response.text == 'The authorization header must start with `Bearer `'


def test_jwt(client):
    response = client.get('/has-data', headers={'Authorization': f'Bearer {TEST_TOKEN}'})
    assert response.status_code == 200


def test_jwt_incorrect(client):
    response = client.get('/has-data', headers={'Authorization': f'Bearer SomeIncorrectToken'})
    assert response.status_code == 401
    assert response.text == 'Invalid authentication token'

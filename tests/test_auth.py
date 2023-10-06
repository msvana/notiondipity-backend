from base import aiotest, client, db, TEST_TOKEN

assert client, db


@aiotest
async def test_no_token(client):
    response = await client.get('/has-data')
    assert response.status_code == 401
    assert await response.get_data(True) == 'No authorization header present'


@aiotest
async def test_no_bearer(client):
    response = await client.get('/has-data', headers={'Authorization': 'Something'})
    assert response.status_code == 401
    assert await response.get_data(True) == 'The authorization header must start with `Bearer `'


@aiotest
async def test_jwt(client):
    response = await client.get('/has-data', headers={'Authorization': f'Bearer {TEST_TOKEN}'})
    assert response.status_code == 200


@aiotest
async def test_jwt_incorrect(client):
    response = await client.get('/has-data', headers={'Authorization': f'Bearer SomeIncorrectToken'})
    assert response.status_code == 401
    assert await response.get_data(True) == 'Invalid authentication token'

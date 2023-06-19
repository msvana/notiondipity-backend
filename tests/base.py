import os

from pytest import fixture

from main import app

TEST_TOKEN = os.environ.get('TEST_TOKEN')

TEST_HEADERS = {
    'Authorization': f'Bearer {TEST_TOKEN}',
    'Content-Type': 'application/json'
}


@fixture
def client():
    return app.test_client()

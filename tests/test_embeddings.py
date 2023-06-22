from datetime import datetime

from base import client, db, TEST_HEADERS

assert client, db


def test_not_has_data(client):
    response = client.get('/has-data', headers=TEST_HEADERS)
    assert response.status_code == 200
    assert response.json['status'] == 'OK'
    assert response.json['hasData'] is False


def test_has_data(client, db):
    cursor = db.cursor()
    cursor.execute("INSERT INTO last_updates VALUES ('b18801e0-dc26-4fbf-8fdf-963d25f44590', '2023-06-19 10:38:23', 1)")
    db.commit()
    response = client.get('/has-data', headers=TEST_HEADERS)
    assert response.status_code == 200
    assert response.json['status'] == 'OK'
    assert response.json['hasData'] is True


def test_refresh_too_soon(client, db):
    cursor = db.cursor()
    now = datetime.now()
    cursor.execute("INSERT INTO last_updates VALUES ('b18801e0-dc26-4fbf-8fdf-963d25f44590', %s, 1)", [now])
    db.commit()
    response = client.get('/refresh-embeddings', headers=TEST_HEADERS)
    assert response.status_code == 425
    assert response.json['status'] == 'error'


def test_resfresh(client, db):
    cursor = db.cursor()
    response = client.get('/refresh-embeddings', headers=TEST_HEADERS)
    assert response.status_code == 200
    assert response.json['status'] == 'OK'
    cursor.execute(
        'SELECT COUNT(*) AS cnt FROM embeddings WHERE user_id = %s', ['b18801e0-dc26-4fbf-8fdf-963d25f44590'])
    num_rows = cursor.fetchone()[0]
    assert num_rows > 50

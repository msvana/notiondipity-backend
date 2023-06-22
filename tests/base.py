import os

import psycopg2
from pytest import fixture

from main import app

TEST_TOKEN = os.environ.get('TEST_TOKEN')

TEST_HEADERS = {
    'Authorization': f'Bearer {TEST_TOKEN}',
    'Content-Type': 'application/json'
}


@fixture
def db():
    connection = psycopg2.connect(
        host='10.252.1.1',
        port='10002',
        user='postgres',
        password='postgresDevPasswordNew',
        database='notiondipity')

    cursor = connection.cursor()
    with open('sql/drop_tables.sql') as drop_tables_script:
        cursor.execute(drop_tables_script.read())
    with open('sql/create_tables.sql') as create_tables_script:
        cursor.execute(create_tables_script.read())
    with open('sql/test_data.sql') as test_data_script:
        cursor.execute(test_data_script.read())

    connection.commit()
    return connection


@fixture
def client(db):
    app.config['db'] = db
    yield app.test_client()

    cursor = db.cursor()
    with open('sql/drop_tables.sql') as drop_tables_script:
        cursor.execute(drop_tables_script.read())
    db.commit()
    db.close()

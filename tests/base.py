import asyncio
import os
from functools import wraps

import psycopg_pool
from pytest import fixture

from main import app

TEST_TOKEN = os.environ.get('TEST_TOKEN')

TEST_HEADERS = {
    'Authorization': f'Bearer {TEST_TOKEN}',
    'Content-Type': 'application/json'
}


def aiotest(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(func(*args, **kwargs))
    return wrapper


@fixture
def db():
    conninfo = f"host=127.0.0.1 " \
               f"port=10001 " \
               f"user=postgres " \
               f"password=LpMTwZtmGa2U4rR " \
               f"dbname=notiondipity_autotest "

    pool = psycopg_pool.ConnectionPool(conninfo)
    with pool.connection() as conn:
        cursor = conn.cursor()
        with open('sql/drop_tables.sql') as drop_tables_script:
            cursor.execute(drop_tables_script.read())
        with open('sql/create_tables.sql') as create_tables_script:
            cursor.execute(create_tables_script.read())
        with open('sql/test_data.sql') as test_data_script:
            cursor.execute(test_data_script.read())

        conn.commit()
    return pool


@fixture
def client(db):
    app.config['db'] = db
    yield app.test_client()

    with db.connection() as conn:
        cursor = conn.cursor()
        with open('sql/drop_tables.sql') as drop_tables_script:
            cursor.execute(drop_tables_script.read())
        conn.commit()

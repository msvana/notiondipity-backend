import asyncio
import os
from datetime import datetime, timedelta
from functools import wraps

import psycopg_pool
from psycopg.cursor import Cursor
from pytest import fixture

from main import app
from notiondipity_backend.resources import embeddings
from notiondipity_backend.utils import PostgresConnectionProvider

TEST_TOKEN = os.environ.get('TEST_TOKEN')
TEST_USER_ID_HASH = '22d195198acb6e3e9e88d3c88c7980aaeed170615269153719cbd16de455c921'

TEST_HEADERS = {
    'Authorization': f'Bearer {TEST_TOKEN}',
    'Content-Type': 'application/json'
}


def aiotest(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        asyncio.run(func(*args, **kwargs))

    return wrapper


@fixture
def db():
    conninfo = f"host=127.0.0.1 " \
               f"port=10001 " \
               f"user=postgres " \
               f"password=LpMTwZtmGa2U4rR " \
               f"dbname=notiondipity_autotest"

    connection_provider = PostgresConnectionProvider(conninfo)
    with connection_provider.connection() as conn:
        cursor = conn.cursor()
        with open('sql/drop_tables.sql') as drop_tables_script:
            cursor.execute(drop_tables_script.read())
        with open('sql/create_tables.sql') as create_tables_script:
            cursor.execute(create_tables_script.read())
        asyncio.run(insert_test_data(cursor))
        conn.commit()
    return connection_provider


@fixture
def client(db):
    app.config['db'] = db
    yield app.test_client()

    with db.connection() as conn:
        cursor = conn.cursor()
        with open('sql/drop_tables.sql') as drop_tables_script:
            cursor.execute(drop_tables_script.read())
        conn.commit()


async def insert_test_data(cursor: Cursor):
    pages = [
        ('a80b1e5a5c8f440da67047680b2f82ce', 'tests/data/page_working_with_arbitrary_sources.md'),
        ('e9e0ef1c8cf84450b286020d76d24f1e', 'tests/data/page_lexical_resources.md'),
        ('ebc5adb46616447f883646215ccd62da', 'tests/data/page_the_crumbling_of_time.md'),
        ('c87b726b4e624a23946b87da90deac0f', 'tests/data/page_world_without_time.md'),
        ('4394b140d956421c97f4e7d9e89418e5', 'tests/data/page_sources_of_time.md'),
    ]

    user_id_hash = '22d195198acb6e3e9e88d3c88c7980aaeed170615269153719cbd16de455c921'
    user_id = '48c73c5c-0d53-4383-83e8-2ef1bfbebe4e'
    date_last_updated = datetime.now() - timedelta(days=2)
    embedding_last_updated = datetime.now() - timedelta(days=1)

    for page in pages:
        with open(page[1], 'r') as page_fd:
            page_text = page_fd.read()
            page_title = page_text.splitlines()[0]
            embedding = (await embeddings.get_embedding(page_text)).tobytes()
            page_record = embeddings.PageEmbeddingRecord(
                page[0], user_id_hash, page[1], page_title,
                embedding, date_last_updated, embedding_last_updated)
            page_record.add_text(user_id, page_text)
            embeddings.add_embedding_record(cursor, page_record)

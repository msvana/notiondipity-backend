import os

import psycopg2
import psycopg2.extensions


def create_postgres_connection() -> tuple[psycopg2.extensions.connection, psycopg2.extensions.cursor]:
    conn: psycopg2.extensions.connection = psycopg2.connect(
        host=os.environ.get('PG_HOST'),
        port=os.environ.get('PG_PORT'),
        user=os.environ.get('PG_USER'),
        password=os.environ.get('PG_PASSWORD'),
        database='postgres')
    return conn, conn.cursor()

from datetime import datetime, timedelta
from functools import wraps

from flask import request
import psycopg2.extensions


def extract_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        authorization_header = request.headers.get('Authorization', None)
        if authorization_header is None:
            return 'No authorization header present', 401
        if not authorization_header.lower().startswith('bearer'):
            return 'The authorization header must start with `Bearer `', 401
        access_token = authorization_header.split(' ', 1)[1].strip()
        if len(access_token) != 50:
            return 'Expected access token of length 32', 401
        return func(*args, **kwargs, access_token = access_token)
    return wrapper


def get_last_updated_time(cursor: psycopg2.extensions.cursor, user_id: str) -> datetime:
    cursor.execute('SELECT * FROM last_updates WHERE user_id = %s LIMIT 1', (user_id,))
    last_updated_record = cursor.fetchone()
    if last_updated_record is None:
        return datetime.now() - timedelta(days=1)
    return last_updated_record[1]


def update_last_updated_time(cursor: psycopg2.extensions.cursor, user_id: str):
    cursor.execute('UPDATE last_updates SET last_update = %s WHERE user_id = %s', (datetime.now(), user_id))
    if cursor.rowcount == 0:
        cursor.execute('INSERT INTO last_updates VALUES (%s, %s)', (user_id, datetime.now()))

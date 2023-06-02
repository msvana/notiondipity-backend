from datetime import datetime, timedelta
from functools import wraps

import jwt
import psycopg2.extensions
from flask import request

from notiondipity_backend.config import JWT_SECRET
from notiondipity_backend.notion import get_user_id


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        authorization_header = request.headers.get('Authorization', None)
        if authorization_header is None:
            return 'No authorization header present', 401
        if not authorization_header.lower().startswith('bearer'):
            return 'The authorization header must start with `Bearer `', 401
        auth_token = authorization_header.split(' ', 1)[1].strip()

        # Legacy authentication
        if len(auth_token) == 50:
            try:
                user_id = get_user_id(auth_token)
                user_info = {'user_id': user_id, 'access_token': auth_token}
                return func(*args, **kwargs, user=user_info)
            except IOError:
                return 'Invalid authentication token', 401

        # New authentication
        try:
            user_info = jwt.decode(auth_token, JWT_SECRET, algorithms=['HS256'])
            return func(*args, **kwargs, user=user_info)
        except jwt.DecodeError:
            return 'Invalid authentication token', 401

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


def has_finished_update(cursor: psycopg2.extensions.cursor, user_id: str) -> bool:
    cursor.execute('SELECT * FROM last_updates WHERE user_id = %s AND finished = 1 LIMIT 1', (user_id,))
    return cursor.rowcount > 0


def mark_finished_update(cursor: psycopg2.extensions.cursor, user_id: str):
    cursor.execute('UPDATE last_updates SET finished = 1 WHERE user_id = %s', (user_id,))

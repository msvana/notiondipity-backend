import os
from functools import wraps
from hashlib import sha256
from typing import Optional

import jwt
import psycopg
import psycopg_pool
from quart import request

from notiondipity_backend.config import JWT_SECRET


class PostgresConnectionProvider:

    def __init__(self):
        self.conninfo = f"host={os.environ.get('PG_HOST')} " \
                        f"port={os.environ.get('PG_PORT')} " \
                        f"user={os.environ.get('PG_USER')} " \
                        f"password={os.environ.get('PG_PASSWORD')} " \
                        f"dbname={os.environ.get('PG_DB', 'postgres')} "

    def connection(self) -> Optional[psycopg.Connection]:
        try:
            return psycopg.connect(self.conninfo)
        except psycopg.OperationalError as e:
            print(e)
            return None


def create_postgres_connection_pool() -> Optional[psycopg_pool.ConnectionPool]:
    try:
        conninfo = f"host={os.environ.get('PG_HOST')} " \
                   f"port={os.environ.get('PG_PORT')} " \
                   f"user={os.environ.get('PG_USER')} " \
                   f"password={os.environ.get('PG_PASSWORD')} " \
                   f"dbname={os.environ.get('PG_DB', 'postgres')} "
        pool = psycopg_pool.ConnectionPool(conninfo)
    except psycopg.OperationalError:
        return None
    return pool


def authenticate(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        authorization_header = request.headers.get('Authorization', None)
        if authorization_header is None:
            return 'No authorization header present', 401
        if not authorization_header.lower().startswith('bearer'):
            return 'The authorization header must start with `Bearer `', 401
        auth_token = authorization_header.split(' ', 1)[1].strip()

        try:
            user_info = jwt.decode(auth_token, JWT_SECRET, algorithms=['HS256'])
            user_info['user_id_hash'] = sha256(user_info['user_id'].encode()).hexdigest()
            print(user_info)
            return await func(*args, **kwargs, user=user_info)
        except jwt.DecodeError:
            return 'Invalid authentication token', 401

    return wrapper

import os
from functools import wraps

import jwt
import psycopg2
import psycopg2.extensions
from flask import request

from notiondipity_backend.config import JWT_SECRET


def create_postgres_connection() -> psycopg2.extensions.connection:
    conn: psycopg2.extensions.connection = psycopg2.connect(
        host=os.environ.get('PG_HOST'),
        port=os.environ.get('PG_PORT'),
        user=os.environ.get('PG_USER'),
        password=os.environ.get('PG_PASSWORD'),
        database='postgres')
    return conn


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        authorization_header = request.headers.get('Authorization', None)
        if authorization_header is None:
            return 'No authorization header present', 401
        if not authorization_header.lower().startswith('bearer'):
            return 'The authorization header must start with `Bearer `', 401
        auth_token = authorization_header.split(' ', 1)[1].strip()

        try:
            user_info = jwt.decode(auth_token, JWT_SECRET, algorithms=['HS256'])
            return func(*args, **kwargs, user=user_info)
        except jwt.DecodeError:
            return 'Invalid authentication token', 401

    return wrapper

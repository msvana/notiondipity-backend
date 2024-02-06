from functools import wraps
from hashlib import md5, sha256
import os
from typing import Optional

from Crypto.Cipher import ChaCha20
import jwt
from pgvector.psycopg import register_vector
import psycopg
from quart import request

from notiondipity_backend.config import JWT_SECRET


class PostgresConnectionProvider:

    def __init__(self, conninfo=None):
        if conninfo:
            self.conninfo = conninfo
        else:
            self.conninfo = f"host={os.environ.get('PG_HOST')} " \
                            f"port={os.environ.get('PG_PORT')} " \
                            f"user={os.environ.get('PG_USER')} " \
                            f"password={os.environ.get('PG_PASSWORD')} " \
                            f"dbname={os.environ.get('PG_DB', 'postgres')} "

    def connection(self) -> Optional[psycopg.Connection]:
        try:
            conn = psycopg.connect(self.conninfo)
            conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
            register_vector(conn)
            return conn
        except psycopg.OperationalError as e:
            print(e)
            return None


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
            return await func(*args, **kwargs, user=user_info)
        except jwt.DecodeError:
            return 'Invalid authentication token', 401

    return wrapper


def encrypt_text_with_user_id(text: str, user_id: str) -> tuple[bytes, bytes]:
    key = sha256(user_id[::-1].encode()).digest()
    cipher = ChaCha20.new(key=key)
    text_encrypted = cipher.encrypt(text.encode())
    return text_encrypted, cipher.nonce


def decrypt_text_with_user_id(text_encrypted: bytes, nonce: bytes, user_id: str) -> str:
    key = sha256(user_id[::-1].encode()).digest()
    cipher = ChaCha20.new(key=key, nonce=nonce)
    return cipher.decrypt(text_encrypted).decode()


def cache_id_from_page_ids(page_ids: list[str]) -> str:
    page_ids_clean = sorted([str(p).replace('-', '') for p in page_ids])
    page_ids_string = " ".join(page_ids_clean)
    cache_id = md5(page_ids_string.encode()).hexdigest()
    return cache_id

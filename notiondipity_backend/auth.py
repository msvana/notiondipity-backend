from functools import wraps

import jwt
from flask import request

from notiondipity_backend.config import JWT_SECRET
from notiondipity_backend.resources.notion import get_user_id


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

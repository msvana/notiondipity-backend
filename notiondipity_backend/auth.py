from flask import request

def extract_token(func):
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


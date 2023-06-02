import flask
import jwt

from notiondipity_backend import config
from notiondipity_backend import notion

auth_api = flask.Blueprint('auth_api', __name__)


@auth_api.route('/v1/token/', methods=['POST'])
def token_v1():
    code = flask.request.json['code']
    redirect_uri = flask.request.json['redirectUri']

    try:
        access_token = notion.get_access_token(code, redirect_uri)
        jwt_token = jwt.encode(
            {'access_token': access_token, 'user_id': notion.get_user_id(access_token)}, config.JWT_SECRET)
        return {'token': jwt_token}
    except IOError as e:
        return str(e), 500


@auth_api.route('/token/', methods=['POST'])
def token():
    code = flask.request.json['code']
    redirect_uri = flask.request.json['redirectUri']

    try:
        access_token = notion.get_access_token(code, redirect_uri)
        return {'accessToken': access_token}
    except IOError as e:
        return str(e), 500

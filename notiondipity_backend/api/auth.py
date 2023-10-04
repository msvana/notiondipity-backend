import quart
import jwt

from notiondipity_backend import config
from notiondipity_backend.resources import notion

auth_api = quart.Blueprint('auth_api', __name__)


@auth_api.route('/v1/token/', methods=['POST'])
async def token():
    json = await quart.request.get_json()
    code = json['code']
    redirect_uri = json['redirectUri']

    try:
        access_token = notion.get_access_token(code, redirect_uri)
        jwt_token = jwt.encode(
            {'access_token': access_token, 'user_id': notion.get_user_id(access_token)}, config.JWT_SECRET)
        return {'token': jwt_token}
    except IOError as e:
        return str(e), 500

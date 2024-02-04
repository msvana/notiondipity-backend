import aiohttp
from quart import Quart, request, Response
from quart_cors import cors

from notiondipity_backend.api.auth import auth_api
from notiondipity_backend.api.embeddingsdb import embeddingsdb_api
from notiondipity_backend.api.ideas import ideas_api
from notiondipity_backend.api.recommend import recommend_api
from notiondipity_backend.config import MIXPANEL_TOKEN
from notiondipity_backend.utils import PostgresConnectionProvider

app = Quart(__name__)
app.config['db'] = PostgresConnectionProvider()
app.register_blueprint(auth_api)
app.register_blueprint(embeddingsdb_api)
app.register_blueprint(ideas_api)
app.register_blueprint(recommend_api)
cors(app)


@app.before_request
async def basic_authentication():
    if request.method.lower() == 'options':
        return Response()
    else:
        app.add_background_task(track_url)


async def track_url():
    event = {
        'event': 'visit',
        'properties': {
            'url': request.base_url,
            'path': request.path,
            'host': request.host,
            'distinct_id': 'anonymous',
            'token': MIXPANEL_TOKEN,
        }
    }
    async with (aiohttp.ClientSession() as session):
        await session.post(
            'https://api.mixpanel.com/track', headers={'Content-Type': 'application/json'}, json=[event])

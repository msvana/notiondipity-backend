import logging

from flask import Flask, request, Response
from flask_cors import CORS

from notiondipity_backend.api.auth import auth_api
from notiondipity_backend.api.embeddingsdb import embeddingsdb_api
from notiondipity_backend.api.ideas import ideas_api
from notiondipity_backend.api.recommend import recommend_api
from notiondipity_backend.utils import PostgresConnectionProvider

app = Flask(__name__)
app.config['db'] = PostgresConnectionProvider()
app.register_blueprint(recommend_api)
app.register_blueprint(auth_api)
app.register_blueprint(embeddingsdb_api)
app.register_blueprint(ideas_api)
CORS(app)


@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()


def main():
    logging.getLogger().setLevel(logging.INFO)
    app.run(host='0.0.0.0', debug=True, port=5001)


if __name__ == '__main__':
    main()

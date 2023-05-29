from datetime import datetime

import flask

from notiondipity_backend import auth, embeddings, notion
from notiondipity_backend.utils import create_postgres_connection

recommend_api = flask.Blueprint('recommend_api', __name__)


@recommend_api.route('/v1/recommend/<page_id>', methods=['POST', 'OPTIONS'])
@auth.extract_token
def recommend(page_id: str, access_token: str):
    page_title: str = flask.request.json['title']
    _, cursor = create_postgres_connection()
    try:
        start_time = datetime.now()
        user_id = notion.get_user_id(access_token)
        print('User Info:', datetime.now() - start_time)
        page_text = f'{page_title} {notion.get_page_text(page_id, access_token)}'
        print('Current page data:', datetime.now() - start_time)
        page_embedding = embeddings.get_embedding(page_text)
        print('Page embedding:', datetime.now() - start_time)
        similar_pages = embeddings.find_closest(cursor, user_id, page_embedding)
        print('Finding closest', datetime.now() - start_time)
        similar_pages = list(
            filter(lambda p: page_id.replace('-', '') not in p[0].page_url, similar_pages))
        similar_pages = [(p[0].page_url, p[0].page_title, p[1]) for p in similar_pages[:7]]
        return {
            'currentPage': {'title': page_title, 'id': page_id},
            'recommendations': similar_pages
        }
    except IOError as e:
        error_string = str(e)
        if error_string.endswith('404'):
            return {'status': 'error', 'error': 'Not found'}, 404
        return str(e), 500

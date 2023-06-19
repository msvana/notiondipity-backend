from datetime import datetime

import flask

import notiondipity_backend.utils
from notiondipity_backend.resources import notion, embeddings
from notiondipity_backend.utils import create_postgres_connection

recommend_api = flask.Blueprint('recommend_api', __name__)


@recommend_api.route('/v1/recommend/<page_id>', methods=['POST'])
@notiondipity_backend.utils.authenticate
def recommend_v1(page_id: str, user: dict):
    page_title: str = flask.request.json['title']
    page_text: str = flask.request.json['content']
    _, cursor = create_postgres_connection()
    try:
        start_time = datetime.now()
        page_text = f'{page_title} {page_text}'
        page_embedding = embeddings.get_embedding(page_text)
        print('Page embedding:', datetime.now() - start_time)
        similar_pages = embeddings.find_closest(cursor, user['user_id'], page_embedding)
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


@recommend_api.route('/recommend/<page_id>')
@notiondipity_backend.utils.authenticate
def recommend(page_id: str, user: dict):
    _, cursor = create_postgres_connection()
    try:
        user_id, access_token = user['user_id'], user['access_token']
        current_page = notion.get_page_info(page_id, access_token)
        page_text = notion.get_page_text(page_id, access_token)
        page_embedding = embeddings.get_embedding(page_text)
        similar_pages = embeddings.find_closest(cursor, user_id, page_embedding)
        similar_pages = list(
            filter(lambda p: p[0].page_url != current_page['url'], similar_pages))
        similar_pages = [(p[0].page_url, p[0].page_title, p[1]) for p in similar_pages[:7]]
        return {
            'currentPage': current_page,
            'recommendations': similar_pages
        }
    except IOError as e:
        error_string = str(e)
        if error_string.endswith('404'):
            return {'status': 'error', 'error': 'Not found'}, 404
        return str(e), 500

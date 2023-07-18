import flask

from notiondipity_backend.resources import embeddings
from notiondipity_backend.utils import authenticate

recommend_api = flask.Blueprint('recommend_api', __name__)


@recommend_api.route('/v2/recommend/', methods=['POST'])
@authenticate
def recommend_v2(user: dict):
    cursor = flask.current_app.config['db']().cursor()
    page_title: str = flask.request.json['title']
    page_text: str = flask.request.json['content']
    page_id: str = flask.request.json.get('pageId')

    page_text = f'{page_title} {page_text}'
    page_embedding = embeddings.get_embedding(page_text)
    similar_pages = embeddings.find_closest(cursor, user['user_id_hash'], page_embedding)
    if page_id:
        similar_pages = [p for p in similar_pages if page_id.replace('-', '') not in p[0].page_url]
    similar_pages = [(p[0].page_url, p[0].page_title, p[1]) for p in similar_pages[:7]]
    return {'status': 'OK', 'recommendations': similar_pages}


@recommend_api.route('/v1/recommend/<page_id>', methods=['POST'])
@authenticate
def recommend_v1(page_id: str, user: dict):
    cursor = flask.current_app.config['db']().cursor()
    page_title: str = flask.request.json['title']
    page_text: str = flask.request.json['content']
    try:
        page_text = f'{page_title} {page_text}'
        page_embedding = embeddings.get_embedding(page_text)
        similar_pages = embeddings.find_closest(cursor, user['user_id_hash'], page_embedding)
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

import flask

from notiondipity_backend.resources import embeddings
from notiondipity_backend.resources import gpt
from notiondipity_backend.utils import authenticate

ideas_api = flask.Blueprint('ideas_api', __name__)


@ideas_api.route('/ideas/', methods=['POST'])
@authenticate
def ideas(user):
    page_title: str = flask.request.json['title']
    page_text: str = flask.request.json['content']
    page_id: str = flask.request.json.get('pageId')
    page_text = f'{page_title} {page_text}'
    page_embedding = embeddings.get_embedding(page_text)
    with flask.current_app.config['db'].connection() as conn, conn.cursor() as cursor:
        similar_pages = embeddings.find_closest(cursor, user['user_id_hash'], page_embedding)
        similar_pages = [p for p in similar_pages if p[0].get_text(user['user_id']) is not None]
        if page_id:
            similar_pages = [p for p in similar_pages if page_id.replace('-', '') not in p[0].page_url]
            similar_pages = embeddings.penalize_relatives(cursor, user['user_id_hash'], page_id, similar_pages)
    idea_suggestions = gpt.get_ideas([page_text] + [p[0].get_text(user['user_id']) for p in similar_pages[:2]])
    return {'status': 'OK', 'ideas': idea_suggestions}

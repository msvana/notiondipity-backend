import quart

from notiondipity_backend.resources import embeddings
from notiondipity_backend.utils import authenticate

recommend_api = quart.Blueprint('recommend_api', __name__)


@recommend_api.route('/v2/recommend/', methods=['POST'])
@authenticate
async def recommend(user: dict):
    json = await quart.request.get_json()
    page_title: str = json['title']
    page_text: str = json['content']
    page_id: str = json.get('pageId')
    page_text = f'{page_title} {page_text}'
    page_embedding = embeddings.get_embedding(page_text)
    with quart.current_app.config['db'].connection() as conn, conn.cursor() as cursor:
        similar_pages = embeddings.find_closest(cursor, user['user_id_hash'], page_embedding)
        if page_id:
            similar_pages = [p for p in similar_pages if page_id.replace('-', '') not in p[0].page_url]
            similar_pages = embeddings.penalize_relatives(cursor, user['user_id_hash'], page_id, similar_pages)
        similar_pages = [(p[0].page_url, p[0].page_title, p[1]) for p in similar_pages[:7]]
    return {'status': 'OK', 'recommendations': similar_pages}

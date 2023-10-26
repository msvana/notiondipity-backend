import uuid
from dataclasses import asdict
import quart

from notiondipity_backend.resources import embeddings
from notiondipity_backend.services import comparison
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
    page_embedding = await embeddings.get_embedding(page_text)
    with quart.current_app.config['db'].connection() as conn, conn.cursor() as cursor:
        similar_pages = embeddings.find_closest(cursor, user['user_id_hash'], page_embedding)
        if page_id:
            page_id_uuid = uuid.UUID(page_id)
            similar_pages = [p for p in similar_pages if page_id_uuid != p[0].page_id]
            similar_pages = embeddings.penalize_relatives(cursor, user['user_id_hash'], page_id, similar_pages)
        similar_pages = [(p[0].page_url, p[0].page_title, p[1]) for p in similar_pages[:7]]
    return {'status': 'OK', 'recommendations': similar_pages}


@recommend_api.route('/compare/', methods=['POST'])
@authenticate
async def compare(user: dict):
    json = await quart.request.get_json()
    page_title: str = json['title']
    page_text: str = json['content']
    page_id: str = json['pageId']
    second_page_id: str = json['secondPageId']

    with quart.current_app.config['db'].connection() as conn, conn.cursor() as cursor:
        current_page_embedding = (await embeddings.get_embedding(f'{page_title}\n{page_text}')).tobytes()
        current_page = embeddings.PageEmbeddingRecord(
            page_id, user['user_id_hash'], '', page_title, current_page_embedding, None, None)
        current_page.add_text(user['user_id'], page_text)
        second_page = embeddings.get_embedding_record(cursor, user['user_id_hash'], second_page_id)
        if second_page:
            comp = await comparison.compare_pages(cursor, user['user_id'], [current_page, second_page])
            if comp:
                return {'status': 'OK', 'comparison': asdict(comp)}
        return {'status': 'NOT_FOUND'}, 404

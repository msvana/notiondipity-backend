import quart
from openai import AsyncOpenAI
from dataclasses import asdict

from notiondipity_backend.resources import embeddings
from notiondipity_backend.services.ideas import IdeaService
from notiondipity_backend.utils import authenticate

ideas_api = quart.Blueprint('ideas_api', __name__)


@ideas_api.route('/ideas/', methods=['POST'])
@authenticate
async def ideas(user):
    json = await quart.request.get_json()
    page_title: str = json['title']
    page_text: str = json['content']
    page_id: str = json.get('pageId')
    page_text = f'{page_title} {page_text}'
    page_embedding = await embeddings.get_embedding(page_text)

    with quart.current_app.config['db'].connection() as conn, conn.cursor() as cursor:
        similar_pages = embeddings.find_closest(cursor, user['user_id_hash'], page_embedding)
        similar_pages = [p for p in similar_pages if p[0].get_text(user['user_id']) is not None]
        if page_id:
            similar_pages = [p for p in similar_pages if page_id.replace('-', '') not in p[0].page_url]
            similar_pages = embeddings.penalize_relatives(cursor, user['user_id_hash'], page_id, similar_pages)

        current_page_embedding = embeddings.PageEmbeddingRecord(
            page_id=page_id,
            user_id=user['user_id'],
            page_title=page_title,
            page_url="",
            embedding_bytes=page_embedding.tobytes(),
            page_last_updated=None,
            embedding_last_updated=None)
        current_page_embedding.add_text(user['user_id'], page_text)

        similar_pages.insert(0, (current_page_embedding, 1.0))
        cached_ideas_service = IdeaService(cursor, AsyncOpenAI())
        idea_suggestions = await cached_ideas_service.get_ideas(user['user_id'], [p[0] for p in similar_pages[:3]])

        # Older versions of the extensions expect a `desc` field
        idea_suggestions_formatted = []
        for idea in idea_suggestions:
            idea_dict = asdict(idea)
            idea_dict['desc'] = idea.description
            idea_suggestions_formatted.append(idea_dict)
    return {'status': 'OK', 'ideas': idea_suggestions_formatted}

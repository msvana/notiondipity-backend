from dataclasses import asdict

from openai import AsyncOpenAI
import quart

from notiondipity_backend.resources import embeddings
from notiondipity_backend.services.ideas import IdeaService
from notiondipity_backend.services.similar_pages import SimilarPagesService
from notiondipity_backend.utils import authenticate

ideas_api = quart.Blueprint('ideas_api', __name__)


@ideas_api.route('/ideas/', methods=['POST'])
@authenticate
async def ideas(user):
    json = await quart.request.get_json()
    page_title: str = json['title']
    page_text: str = json['content']
    page_id: str = json.get('pageId')
    refresh: bool = json.get('refresh', False)

    page_text = f'{page_title} {page_text}'
    page_embedding = await embeddings.get_embedding(page_text)

    with quart.current_app.config['db'].connection() as conn, conn.cursor() as cursor:
        similar_pages_service = SimilarPagesService(cursor)
        similar_pages = similar_pages_service.get_similar_pages(
            page_embedding, user['user_id'], user['user_id_hash'], page_id)[:2]

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
        ideas_service = IdeaService(cursor, AsyncOpenAI())

        if refresh:
            idea_suggestions = await ideas_service.regenerate_and_store_ideas(
                user['user_id'], [p[0] for p in similar_pages])
        else:
            idea_suggestions = await ideas_service.get_ideas(user['user_id'], [p[0] for p in similar_pages])

        # Older versions of the extensions expect a `desc` field
        idea_suggestions_formatted = []
        for idea in idea_suggestions:
            idea_dict = asdict(idea)
            idea_dict['desc'] = idea.description
            idea_suggestions_formatted.append(idea_dict)
    return {'status': 'OK', 'ideas': idea_suggestions_formatted}

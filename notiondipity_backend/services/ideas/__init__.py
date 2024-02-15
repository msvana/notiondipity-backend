from openai import AsyncOpenAI
from psycopg.cursor import Cursor

from notiondipity_backend.resources.embeddings import PageEmbeddingRecord
from notiondipity_backend.services.comparisons import ComparisonService
from notiondipity_backend.utils import cache_id_from_page_ids

from . import generator
from .cache import CachedIdea, IdeaCache
from .idea import Idea


class IdeaService:

    def __init__(self, cursor: Cursor, openai_client: AsyncOpenAI):
        self._openai_client = openai_client
        self._idea_cache = IdeaCache(cursor)
        self._compoarison_service = ComparisonService(openai_client, cursor)

    async def get_ideas(self, user_id: str, pages: list[PageEmbeddingRecord]) -> list[Idea]:
        page_ids = [p.page_id for p in pages]

        if self._idea_cache.is_cache_record_valid(pages):
            cached_ideas = self._idea_cache.get_cached_ideas(page_ids)
            return [self._cached_idea_to_idea(ci, user_id) for ci in cached_ideas]

        self._idea_cache.delete_cached_ideas(page_ids)

        ideas = await generator.get_ideas(self._openai_client, self._compoarison_service, pages, user_id)
        cache_id = cache_id_from_page_ids(page_ids)

        for idea_new in ideas:
            cached_idea = CachedIdea(cache_id=cache_id)
            cached_idea.set_title(idea_new.title, user_id)
            cached_idea.set_description(idea_new.description, user_id)
            self._idea_cache.cache_idea(cached_idea)

        self._idea_cache.cache_embeddings(cache_id, pages)
        return ideas

    @staticmethod
    def _cached_idea_to_idea(cached_idea: CachedIdea, user_id: str) -> Idea:
        idea = Idea(cached_idea.get_title(user_id), cached_idea.get_description(user_id), True)
        return idea
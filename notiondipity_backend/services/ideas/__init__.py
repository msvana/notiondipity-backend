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

        return await self.regenerate_and_store_ideas(user_id, pages)

    async def regenerate_and_store_ideas(self, user_id: str, pages: list[PageEmbeddingRecord]) -> list[Idea]:
        page_ids = [p.page_id for p in pages]
        self._idea_cache.delete_cached_ideas(page_ids)

        ideas = await generator.get_ideas(self._openai_client, self._compoarison_service, pages, user_id)
        cache_id = cache_id_from_page_ids(page_ids)

        for idea_new in ideas:
            cached_idea = CachedIdea(cache_id=cache_id)
            cached_idea.set_title(idea_new.title, user_id)
            cached_idea.set_description(idea_new.description, user_id)
            idea_new.idea_id = self._idea_cache.cache_idea(cached_idea)

        self._idea_cache.cache_embeddings(cache_id, pages)
        return ideas

    def save_idea(self, user_hash: str, idea_id: int):
        is_owner = self._idea_cache.get_owner_hash(idea_id) == user_hash
        if not is_owner:
            raise ValueError('User does not own the idea')
        self._idea_cache.save_idea(idea_id)

    def get_saved_ideas(self, user_hash: str, user_id: str) -> list[Idea]:
        cached_ideas = self._idea_cache.get_saved_ideas(user_hash)
        return [self._cached_idea_to_idea(ci, user_id) for ci in cached_ideas]

    @staticmethod
    def _cached_idea_to_idea(cached_idea: CachedIdea, user_id: str) -> Idea:
        if cached_idea.idea_id is None:
            raise ValueError('Cached idea does not have an idea_id')
        idea = Idea(cached_idea.get_title(user_id), cached_idea.get_description(
            user_id), cached_idea.idea_id, True, cached_idea.saved)
        return idea

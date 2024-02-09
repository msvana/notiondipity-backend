from datetime import datetime
import json

from openai import AsyncOpenAI
from psycopg.cursor import Cursor

from notiondipity_backend.resources.embeddings import PageEmbeddingRecord
from notiondipity_backend.utils import cache_id_from_page_ids

from .cache import CachedComparison, ComparisonCache
from .comparison import Comparison
from . import generator


class ComparisonService:

    def __init__(self, openai_client: AsyncOpenAI, cursor: Cursor):
        self._openai_client = openai_client
        self._comparison_cache = ComparisonCache(cursor)

    async def get_comparisons(self, pages: list[PageEmbeddingRecord], user_id: str) -> Comparison | None:
        page_ids = [p.page_id for p in pages]
        second_page_title = pages[1].page_title

        if self._comparison_cache.is_cache_record_valid(pages):
            comparison_cache_record = self._comparison_cache.get_cached_comparison(page_ids)
            return Comparison(
                **json.loads(comparison_cache_record.get_comparison(user_id)),
                secondPageTitle=second_page_title, cached=True)

        self._comparison_cache.delete_cached_comparison(page_ids)
        comp, _ = await generator.compare_pages(self._openai_client, [(p.page_title, p.get_text(user_id)) for p in pages])

        if comp is None:
            return None

        comp.secondPageTitle = second_page_title
        comparison_cache_record = CachedComparison(
            cache_id_from_page_ids(page_ids), datetime.now())
        comparison_cache_record.set_comparison(json.dumps(comp.cache_dict), user_id)
        self._comparison_cache.cache_comparison(comparison_cache_record, pages)
        return comp

    def get_comparison_prompt(self, pages: list[PageEmbeddingRecord], user_id: str) -> str:
        return generator.get_comparison_prompt([(p.page_title, p.get_text(user_id)) for p in pages])

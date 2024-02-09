from datetime import datetime
import json

from openai import AsyncOpenAI
from psycopg.cursor import Cursor

from notiondipity_backend.resources.embeddings import PageEmbeddingRecord
from notiondipity_backend.services.comparisons.cache import (
    CachedComparison,
    ComparisonCache,
)
from notiondipity_backend.services.comparisons.comparison import Comparison
from notiondipity_backend.services.comparisons.generator import (
    compare_pages as gpt_compare_pages,
)
from notiondipity_backend.utils import cache_id_from_page_ids


async def compare_pages(cursor: Cursor, user_id: str, pages: list[PageEmbeddingRecord]) -> Comparison | None:
    page_ids = [p.page_id for p in pages]
    second_page_title = pages[1].page_title
    comparison_cache = ComparisonCache(cursor)

    if comparison_cache.is_cache_record_valid(pages):
        comparison_cache_record = comparison_cache.get_cached_comparison(page_ids)
        return Comparison(
            **json.loads(comparison_cache_record.get_comparison(user_id)),
            secondPageTitle=second_page_title, cached=True)

    comparison_cache.delete_cached_comparison(page_ids)
    comp, _ = await gpt_compare_pages(AsyncOpenAI(), [(p.page_title, p.get_text(user_id)) for p in pages])

    if comp is None:
        return None

    comp.secondPageTitle = second_page_title
    comparison_cache_record = CachedComparison(
        cache_id_from_page_ids(page_ids), datetime.now())

    comp_stored = {
        'similarities': comp.similarities,
        'differences': comp.differences,
        'combinations': comp.combinations
    }

    comparison_cache_record.set_comparison(json.dumps(comp_stored), user_id)
    comparison_cache.cache_comparison(comparison_cache_record, pages)
    return comp

from datetime import datetime
import json

from psycopg.cursor import Cursor

from notiondipity_backend.resources import comparison
from notiondipity_backend.resources.embeddings import PageEmbeddingRecord
from notiondipity_backend.resources.gpt.comparisons import Comparison, compare_pages


async def compare_pages(cursor: Cursor, user_id: str, pages: list[PageEmbeddingRecord]) -> Comparison | None:
    page_ids = [p.page_id for p in pages]
    second_page_title = pages[1].page_title

    if comparison.is_comparison_cache_record_valid(cursor, pages):
        comparison_cache_record = comparison.get_comparison_cache_record(cursor, page_ids)
        return Comparison(
            **json.loads(comparison_cache_record.get_comparison(user_id)),
            secondPageTitle=second_page_title, cached=True)

    comparison.delete_comparison_cache_record(cursor, page_ids)
    comp, _ = await compare_pages([(p.page_title, p.get_text(user_id)) for p in pages])

    if comp is None:
        return None

    comp.secondPageTitle = second_page_title
    comparison_cache_record = comparison.ComparisonCacheRecord(
        comparison.comparison_id_from_page_ids(page_ids), datetime.now())
    comparison_cache_record.set_comparison(json.dumps(comp), user_id)
    comparison.add_comparison_cache_record(cursor, comparison_cache_record, pages)
    return comp

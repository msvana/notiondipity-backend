import json
from dataclasses import dataclass
from datetime import datetime

from psycopg.cursor import Cursor

from notiondipity_backend.resources import comparison
from notiondipity_backend.resources import embeddings
from notiondipity_backend.resources import gpt


@dataclass
class Comparison:
    similarities: list[str]
    differences: list[str]
    combinations: list[str]
    cached: bool


async def compare_pages(cursor: Cursor, user_id: str,
                        pages: list[embeddings.PageEmbeddingRecord]) -> Comparison | None:
    page_ids = [p.page_id for p in pages]
    if comparison.is_comparison_cache_record_valid(cursor, pages):
        comparison_cache_record = comparison.get_comparison_cache_record(cursor, page_ids)
        return Comparison(**json.loads(comparison_cache_record.get_comparison(user_id)), cached=True)
    comparison.delete_comparison_cache_record(cursor, page_ids)
    comp_raw, _ = await gpt.compare_pages([(p.page_title, p.get_text(user_id)) for p in pages])
    if comp_raw is None:
        return None
    comp = Comparison(**comp_raw, cached=False)
    comparison_cache_record = comparison.ComparisonCacheRecord(
        comparison.comparison_id_from_page_ids(page_ids), datetime.now())
    comparison_cache_record.set_comparison(json.dumps(comp_raw), user_id)
    comparison.add_comparison_cache_record(cursor, comparison_cache_record, pages)
    return comp

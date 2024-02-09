from dataclasses import asdict, dataclass
from datetime import datetime

from psycopg.cursor import Cursor

from notiondipity_backend import utils
from notiondipity_backend.config import CACHE_VALID_DISTANCE_THRESHOLD
from notiondipity_backend.resources.embeddings import PageEmbeddingRecord


@dataclass
class CachedComparison:
    comparison_id: str
    time_updated: datetime
    comparison_nonce: bytes | None = None
    comparison_encrypted: bytes | None = None

    def get_comparison(self, user_id: str) -> str:
        return utils.decrypt_text_with_user_id(self.comparison_encrypted, self.comparison_nonce, user_id)

    def set_comparison(self, comparison: str, user_id: str):
        self.comparison_encrypted, self.comparison_nonce = utils.encrypt_text_with_user_id(comparison, user_id)


class ComparisonCache:

    def __init__(self, cursor: Cursor):
        self._cursor = cursor

    def cache_comparison(self, cached_comparison: CachedComparison, page_embeddings: list[PageEmbeddingRecord]):
        self._cursor.execute('''
            INSERT INTO comparisons VALUES (
                %(comparison_id)s,
                %(time_updated)s,
                %(comparison_nonce)s,
                %(comparison_encrypted)s)
            ''', asdict(cached_comparison))

        for page_embedding in page_embeddings:
            params = (
                cached_comparison.comparison_id,
                page_embedding.clean_page_id,
                page_embedding.embedding)
            self._cursor.execute('INSERT INTO comparison_embeddings VALUES(%s, %s, %s)', params)

    def get_cached_comparison(self, page_ids: list[str]) -> CachedComparison | None:
        comparison_id = utils.cache_id_from_page_ids(page_ids)
        self._cursor.execute('SELECT * FROM comparisons WHERE comparison_id = %s', (comparison_id,))
        result = self._cursor.fetchone()
        return CachedComparison(*result) if result else None

    def is_cache_record_valid(self, page_embeddings: list[PageEmbeddingRecord]) -> bool:
        cache_id = utils.cache_id_from_page_ids([p.page_id for p in page_embeddings])
        for page_embedding in page_embeddings:
            params = (page_embedding.embedding, cache_id, page_embedding.clean_page_id)
            self._cursor.execute('''
                SELECT (embedding <=> %s) AS similarity
                FROM comparison_embeddings WHERE comparison_id = %s AND page_id = %s
                ''', params)
            record = self._cursor.fetchone()
            if not record or record[0] >= CACHE_VALID_DISTANCE_THRESHOLD:
                return False
            return True

    def delete_cached_comparison(self, page_ids: list[str]):
        cache_id = utils.cache_id_from_page_ids(page_ids)
        self._cursor.execute('DELETE FROM comparison_embeddings WHERE comparison_id = %s', (cache_id,))
        self._cursor.execute('DELETE FROM comparisons WHERE comparison_id = %s', (cache_id,))

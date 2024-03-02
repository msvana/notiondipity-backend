from dataclasses import asdict, dataclass
from datetime import datetime

from psycopg.connection import Connection
from psycopg.rows import class_row

from notiondipity_backend import utils
from notiondipity_backend.config import CACHE_VALID_DISTANCE_THRESHOLD
from notiondipity_backend.resources.embeddings import PageEmbeddingRecord


@dataclass
class CachedComparison:
    comparison_id: str
    time_updated: datetime
    comparison_nonce: bytes | None = None
    comparison_encrypted: bytes | None = None

    def get_comparison(self, user_id: str) -> str | None:
        if not self.comparison_encrypted or not self.comparison_nonce:
            return None
        return utils.decrypt_text_with_user_id(self.comparison_encrypted, self.comparison_nonce, user_id)

    def set_comparison(self, comparison: str, user_id: str):
        self.comparison_encrypted, self.comparison_nonce = utils.encrypt_text_with_user_id(comparison, user_id)


class ComparisonCache:

    def __init__(self, connection: Connection):
        self._connection = connection

    def cache_comparison(self, cached_comparison: CachedComparison, page_embeddings: list[PageEmbeddingRecord]):
        with self._connection.cursor() as cursor:
            cursor.execute('''
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
                cursor.execute('INSERT INTO comparison_embeddings VALUES(%s, %s, %s)', params)

    def get_cached_comparison(self, page_ids: list[str]) -> CachedComparison | None:
        comparison_id = utils.cache_id_from_page_ids(page_ids)
        with self._connection.cursor(row_factory=class_row(CachedComparison)) as cursor:
            cursor.execute('SELECT * FROM comparisons WHERE comparison_id = %s', (comparison_id,))
            result = cursor.fetchone()
        return result

    def is_cache_record_valid(self, page_embeddings: list[PageEmbeddingRecord]) -> bool:
        cache_id = utils.cache_id_from_page_ids([p.page_id for p in page_embeddings])
        at_least_one_found = False
        with self._connection.cursor() as cursor:
            for page_embedding in page_embeddings:
                params = (page_embedding.embedding, cache_id, page_embedding.clean_page_id)
                cursor.execute('''
                    SELECT (embedding <=> %s) AS similarity
                    FROM comparison_embeddings WHERE comparison_id = %s AND page_id = %s
                    ''', params)
                record = cursor.fetchone()
                if not record or record[0] >= CACHE_VALID_DISTANCE_THRESHOLD:
                    return False
                at_least_one_found = True
        return at_least_one_found

    def delete_cached_comparison(self, page_ids: list[str]):
        cache_id = utils.cache_id_from_page_ids(page_ids)
        with self._connection.cursor() as cursor:
            cursor.execute('DELETE FROM comparison_embeddings WHERE comparison_id = %s', (cache_id,))
            cursor.execute('DELETE FROM comparisons WHERE comparison_id = %s', (cache_id,))

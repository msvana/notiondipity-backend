from dataclasses import dataclass, asdict
from datetime import datetime
from hashlib import md5

from psycopg.cursor import Cursor

from notiondipity_backend import utils
from notiondipity_backend.config import COMPARISON_VALID_SIMILARITY_THRESHOLD
from notiondipity_backend.resources.embeddings import PageEmbeddingRecord


@dataclass
class ComparisonCacheRecord:
    comparison_id: str
    time_updated: datetime
    comparison_nonce: bytes
    comparison_encrypted: bytes

    def get_comparison(self, user_id: str) -> str:
        return utils.decrypt_text_with_user_id(self.comparison_encrypted, self.comparison_nonce, user_id)

    def set_comparison(self, comparison: str, user_id: str):
        self.comparison_encrypted, self.comparison_nonce = utils.encrypt_text_with_user_id(comparison, user_id)


def add_comparison_cache_record(cursor: Cursor, comparison_cache_record: ComparisonCacheRecord,
                                page_embeddings: list[PageEmbeddingRecord]):
    cursor.execute('''
        INSERT INTO comparisons VALUES (
            %(comparison_id)s, 
            %(time_updated)s, 
            %(comparison_nonce)s, 
            %(comparsion_encrypted)s)
        ''', asdict(comparison_cache_record))

    for page_embedding in page_embeddings:
        params = (
            comparison_cache_record.comparison_id,
            page_embedding.page_id.replace('-', ''),
            page_embedding.embedding)
        cursor.execute('INSERT INTO comparison_embeddings VALUES(%s, %s, %s)', params)


def get_comparison_cache_record(cursor: Cursor, page_ids: list[str]) -> ComparisonCacheRecord | None:
    comparison_id = _comparison_id_from_page_ids(page_ids)
    cursor.execute('SELECT * FROM comparisons WHERE comparison_id = %s', (comparison_id,))
    result = cursor.fetchone()
    return ComparisonCacheRecord(*result) if result else None


def is_comparison_cache_record_valid(cursor: Cursor, page_embeddings: list[PageEmbeddingRecord]) -> bool:
    comparison_id = _comparison_id_from_page_ids([p.page_id for p in page_embeddings])
    for page_embeddings in page_embeddings:
        params = (page_embeddings.embedding, comparison_id, page_embeddings.page_id)
        cursor.execute('''
            SELECT (embedding <=> %s) AS similarity 
            FROM comparison_embeddings WHERE comparison_id = %s AND page_id = %s
            ''', params)
        record = cursor.fetchone()
        if not record or record[0] <= COMPARISON_VALID_SIMILARITY_THRESHOLD:
            return False
    return True


def delete_comparison_cache_record(cursor: Cursor, page_ids: list[str]):
    comparison_id = _comparison_id_from_page_ids(page_ids)
    cursor.execute('DELETE FROM comparison_embeddings WHERE comparison_id = %s', (comparison_id,))
    cursor.execute('DELETE FROM comparison WHERE comparison_id = %s', (comparison_id,))


def _comparison_id_from_page_ids(page_ids: list[str]) -> str:
    page_ids_clean = map(lambda p: p.replace('-', ''), page_ids)
    page_ids_set = set(page_ids_clean)
    comparison_id = md5(str(page_ids_set).encode()).hexdigest()
    return comparison_id

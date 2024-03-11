from dataclasses import asdict, dataclass, field
from datetime import datetime

from psycopg.connection import Connection
from psycopg.rows import class_row

from notiondipity_backend import utils
from notiondipity_backend.config import CACHE_VALID_DISTANCE_THRESHOLD
from notiondipity_backend.resources.embeddings import PageEmbeddingRecord


@dataclass
class CachedIdea:
    cache_id: str
    time_updated: datetime = field(default_factory=datetime.now)
    idea_id: int | None = field(default=None)
    title_nonce: bytes | None = field(default=None)
    title_encrypted: bytes | None = field(default=None)
    description_nonce: bytes | None = field(default=None)
    description_encrypted: bytes | None = field(default=None)
    saved: bool = field(default=False)

    def get_title(self, user_id: str) -> str | None:
        if not self.title_encrypted or not self.title_nonce:
            return None
        return utils.decrypt_text_with_user_id(self.title_encrypted, self.title_nonce, user_id)

    def set_title(self, title: str, user_id: str):
        self.title_encrypted, self.title_nonce = utils.encrypt_text_with_user_id(title, user_id)

    def get_description(self, user_id: str) -> str | None:
        if not self.description_encrypted or not self.description_nonce:
            return None
        return utils.decrypt_text_with_user_id(self.description_encrypted, self.description_nonce, user_id)

    def set_description(self, description: str, user_id: str):
        self.description_encrypted, self.description_nonce = utils.encrypt_text_with_user_id(description, user_id)


class IdeaCache:

    def __init__(self, connection: Connection):
        self._connection = connection

    def cache_idea(self, cached_idea: CachedIdea) -> int:
        with self._connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO ideas (
                    cache_id, 
                    time_updated, 
                    title_nonce, 
                    title_encrypted, 
                    description_nonce, 
                    description_encrypted
                ) VALUES (
                    %(cache_id)s, 
                    %(time_updated)s, 
                    %(title_nonce)s, 
                    %(title_encrypted)s,
                    %(description_nonce)s,
                    %(description_encrypted)s
                ) RETURNING idea_id
                ''', asdict(cached_idea))
            result = cursor.fetchone()
        if not result:
            raise ValueError('Failed to insert idea')
        idea_id = result[0]
        return idea_id

    def cache_embeddings(self, cache_id: str, page_embeddings: list[PageEmbeddingRecord]):
        with self._connection.cursor() as cursor:
            for page_embedding in page_embeddings:
                params = (cache_id, page_embedding.clean_page_id, page_embedding.embedding)
                cursor.execute('INSERT INTO idea_embeddings VALUES(%s, %s, %s)', params)

    def get_cached_ideas(self, page_ids: list[str]) -> list[CachedIdea]:
        cache_id = utils.cache_id_from_page_ids(page_ids)
        with self._connection.cursor(row_factory=class_row(CachedIdea)) as cursor:
            cursor.execute('SELECT * FROM ideas WHERE cache_id = %s', (cache_id,))
            return list(cursor.fetchall())

    def is_cache_record_valid(self, page_embeddings: list[PageEmbeddingRecord]) -> bool:
        cache_id = utils.cache_id_from_page_ids([p.page_id for p in page_embeddings])
        for page_embedding in page_embeddings:
            params = (page_embedding.embedding, cache_id, page_embedding.clean_page_id)
            with self._connection.cursor() as cursor:
                cursor.execute('''
                    SELECT (embedding <=> %s) AS similarity 
                    FROM idea_embeddings WHERE cache_id = %s AND page_id = %s
                    ''', params)
                record = cursor.fetchone()
            if not record or record[0] >= CACHE_VALID_DISTANCE_THRESHOLD:
                return False
        return True

    def get_owner_hash(self, idea_id: int) -> str:
        with self._connection.cursor() as cursor:
            cursor.execute('''
                SELECT e.user_id
                FROM ideas i
                JOIN idea_embeddings ie ON i.cache_id = ie.cache_id
                JOIN embeddings e ON e.page_id = CAST(ie.page_id AS UUID)
                WHERE i.idea_id = %s
                ''', (idea_id,))
            result = cursor.fetchone()
        if not result:
            raise ValueError(f'No record found for idea with ID {idea_id}')
        user_hash = result[0]
        return user_hash

    def save_idea(self, idea_id: int):
        with self._connection.cursor() as cursor:
            cursor.execute('UPDATE ideas SET saved = TRUE WHERE idea_id = %s', (idea_id,))

    def unsave_idea(self, idea_id: int):
        with self._connection.cursor() as cursor:
            cursor.execute('UPDATE ideas SET saved = FALSE WHERE idea_id = %s', (idea_id,))

    def get_saved_ideas(self, user_hash: str):
        with self._connection.cursor(row_factory=class_row(CachedIdea)) as cursor:
            cursor.execute('''
                SELECT DISTINCT ON (i.idea_id) i.*
                FROM ideas i
                JOIN idea_embeddings ie ON i.cache_id = ie.cache_id
                JOIN embeddings e ON e.page_id = CAST(ie.page_id AS UUID)
                WHERE e.user_id = %s AND saved = TRUE
                ''', (user_hash,))
            return list(cursor.fetchall())

    def delete_cached_ideas(self, page_ids: list[str]):
        cache_id = utils.cache_id_from_page_ids(page_ids)
        with self._connection.cursor() as cursor:
            cursor.execute('DELETE FROM idea_embeddings WHERE cache_id = %s', (cache_id,))
            cursor.execute('DELETE FROM ideas WHERE cache_id = %s AND NOT saved', (cache_id,))

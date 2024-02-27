from dataclasses import asdict, dataclass, field
from datetime import datetime

from psycopg.cursor import Cursor

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

    def get_title(self, user_id: str) -> str:
        return utils.decrypt_text_with_user_id(self.title_encrypted, self.title_nonce, user_id)

    def set_title(self, title: str, user_id: str):
        self.title_encrypted, self.title_nonce = utils.encrypt_text_with_user_id(title, user_id)

    def get_description(self, user_id: str) -> str:
        return utils.decrypt_text_with_user_id(self.description_encrypted, self.description_nonce, user_id)

    def set_description(self, description: str, user_id: str):
        self.description_encrypted, self.description_nonce = utils.encrypt_text_with_user_id(description, user_id)


class IdeaCache:

    def __init__(self, cursor: Cursor):
        self._cursor = cursor

    def cache_idea(self, cached_idea: CachedIdea) -> int:
        self._cursor.execute('''
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
        result = self._cursor.fetchone()
        if not result:
            raise ValueError('Failed to insert idea')
        idea_id = result[0]
        return idea_id

    def cache_embeddings(self, cache_id: str, page_embeddings: list[PageEmbeddingRecord]):
        for page_embedding in page_embeddings:
            params = (cache_id, page_embedding.clean_page_id, page_embedding.embedding)
            self._cursor.execute('INSERT INTO idea_embeddings VALUES(%s, %s, %s)', params)

    def get_cached_ideas(self, page_ids: list[str]) -> list[CachedIdea]:
        cache_id = utils.cache_id_from_page_ids(page_ids)
        self._cursor.execute("""
            SELECT 
                cache_id, 
                time_updated, 
                idea_id, 
                title_nonce, 
                title_encrypted, 
                description_nonce, 
                description_encrypted, 
                saved 
            FROM ideas WHERE cache_id = %s""", (cache_id,))
        return [CachedIdea(*result) for result in self._cursor.fetchall()]

    def is_cache_record_valid(self, page_embeddings: list[PageEmbeddingRecord]) -> bool:
        cache_id = utils.cache_id_from_page_ids([p.page_id for p in page_embeddings])
        for page_embedding in page_embeddings:
            params = (page_embedding.embedding, cache_id, page_embedding.clean_page_id)
            self._cursor.execute('''
                SELECT (embedding <=> %s) AS similarity 
                FROM idea_embeddings WHERE cache_id = %s AND page_id = %s
                ''', params)
            record = self._cursor.fetchone()
            if not record or record[0] >= CACHE_VALID_DISTANCE_THRESHOLD:
                return False
        return True

    def get_owner_hash(self, idea_id: int) -> str:
        self._cursor.execute('''
            SELECT e.user_id
            FROM ideas i
            JOIN idea_embeddings ie ON i.cache_id = ie.cache_id
            JOIN embeddings e ON e.page_id = e.page_id
            WHERE i.idea_id = %s
            ''', (idea_id,))
        result = self._cursor.fetchone()
        if not result:
            raise ValueError(f'No record found for idea with ID {idea_id}')
        user_hash = result[0]
        return user_hash

    def save_idea(self, idea_id: int):
        self._cursor.execute('UPDATE ideas SET saved = TRUE WHERE idea_id = %s', (idea_id,))

    def delete_cached_ideas(self, page_ids: list[str]):
        cache_id = utils.cache_id_from_page_ids(page_ids)
        self._cursor.execute('DELETE FROM idea_embeddings WHERE cache_id = %s', (cache_id,))
        self._cursor.execute('DELETE FROM ideas WHERE cache_id = %s AND NOT saved', (cache_id,))

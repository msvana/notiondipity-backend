import numpy as np
from psycopg.cursor import Cursor

from notiondipity_backend.resources import embeddings


class SimilarPagesService:

    def __init__(self, cursor: Cursor):
        self._cursor = cursor

    def get_similar_pages(self, text_embedding: np.ndarray, user_id: str, user_id_hash: str, page_id: str = None):
        similar_pages = embeddings.find_closest(self._cursor, user_id_hash, text_embedding)
        similar_pages = [p for p in similar_pages if p[0].get_text(user_id) is not None]
        if page_id:
            similar_pages = [p for p in similar_pages if page_id.replace('-', '') not in p[0].page_url]
            similar_pages = embeddings.penalize_relatives(self._cursor, user_id_hash, page_id, similar_pages)
        return similar_pages

from dataclasses import dataclass
from datetime import datetime

import numpy as np
import openai
import psycopg2.extensions

from notiondipity_backend.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


@dataclass
class PageEmbeddingRecord:
    page_id: str
    page_url: str
    embedding: np.ndarray
    page_last_updated: datetime | None
    embedding_last_updated: datetime | None
    user_id: str

    def __iter__(self):
        yield from [self.page_id, self.page_url, np.array2string(self.embedding), self.page_last_updated,
                    self.embedding_last_updated, self.user_id]


def add_embedding_record(cursor: psycopg2.extensions.cursor, embedding_record: PageEmbeddingRecord):
    cursor.execute('INSERT INTO embeddings VALUES (%s, %s, %s, %s, %s)',
                   tuple(embedding_record))


def get_embedding_record(cursor: psycopg2.extensions.cursor, user_id: str, page_id: str) -> PageEmbeddingRecord | None:
    cursor.execute(
        'SELECT * FROM embeddings WHERE user_id = %s AND page_id = %s', (user_id, page_id))
    result = cursor.fetchone()
    if result:
        record = list(result)
        record[2] = np.fromstring(record[2].tobytes())  # type: ignore
        return PageEmbeddingRecord(*record)
    return None


def get_all_embedding_records(cursor: psycopg2.extensions.cursor, user_id: str) -> list[PageEmbeddingRecord]:
    cursor.execute('SELECT * FROM embeddings WHERE user_id = %s', (user_id, ))
    page_embeddings_records = []
    for record in cursor.fetchall():
        record = list(record)
        record[2] = np.fromstring(record[2].tobytes())  # type: ignore
        page_embeddings_records.append(PageEmbeddingRecord(*record))
    return page_embeddings_records


def delete_embedding_record(cursor: psycopg2.extensions.cursor, user_id: str, page_id: str):
    cursor.execute(
        'DELETE FROM embeddings WHERE user_id = %s AND page_id = %s', (user_id, page_id))


def delete_removed_records(cursor: psycopg2.extensions.cursor, user_id: str, existing_page_ids: list[str]) -> int:
    page_ids_concat = "','".join(existing_page_ids)
    cursor.execute(
        f"DELETE FROM embeddings WHERE user_id = %s AND page_id NOT IN ('{page_ids_concat}')", (user_id,))
    num_deleted = cursor.rowcount
    return num_deleted


def get_embedding(text: str):
    response = openai.Embedding.create(
        input=text,
        model='text-embedding-ada-002')
    embedding = np.array(response['data'][0]['embedding'])
    return embedding


def find_closest(cursor, user_id: str, embedding) -> list[tuple[PageEmbeddingRecord, float]]:
    page_embeddings_records = get_all_embedding_records(cursor, user_id)
    pages_with_distances = []

    for page_embedding_record in page_embeddings_records:
        distance = np.dot(embedding, page_embedding_record.embedding) \
            / (np.linalg.norm(embedding) * np.linalg.norm(page_embedding_record.embedding))
        pages_with_distances.append((page_embedding_record, distance))
    pages_sorted = sorted(pages_with_distances,
                          key=lambda x: x[1], reverse=True)
    return pages_sorted

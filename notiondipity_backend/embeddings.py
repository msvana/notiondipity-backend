import pickle
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

    def __iter__(self):
        yield from [self.page_id, self.page_url, self.embedding.tostring(), self.page_last_updated,
                    self.embedding_last_updated]


def add_embedding_record(cursor: psycopg2.extensions.cursor, embedding_record: PageEmbeddingRecord):
    cursor.execute('INSERT INTO embeddings VALUES (%s, %s, %s, %s, %s)',
                   tuple(embedding_record))


def get_embedding_record(cursor: psycopg2.extensions.cursor, page_id: str) -> PageEmbeddingRecord | None:
    cursor.execute('SELECT * FROM embeddings WHERE page_id = %s', (page_id,))
    if cursor.rowcount == 0:
        return None
    else:
        record = list(cursor.fetchone())
        record[2] = np.asarray(record[2])
        return PageEmbeddingRecord(*record)


def get_embedding(text: str):
    response = openai.Embedding.create(
        input=text,
        model='text-embedding-ada-002')
    embedding = np.array(response['data'][0]['embedding'])
    return embedding


def find_closest(embedding) -> list:
    embs = pickle.load(open('embs.pickle', 'rb'))
    pages = []
    for url, emb in embs:
        distance = np.dot(embedding, emb) / (np.linalg.norm(embedding) * np.linalg.norm(emb))
        pages.append((url, distance))
    pages_sorted = sorted(pages, key=lambda x: x[1], reverse=True)
    return pages_sorted

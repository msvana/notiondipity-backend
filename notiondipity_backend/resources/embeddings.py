from dataclasses import dataclass, asdict
from datetime import datetime
from hashlib import sha256
from typing import Optional

import aiohttp
import numpy as np
import openai
from Crypto.Cipher import ChaCha20
from psycopg import cursor

from notiondipity_backend.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


@dataclass
class PageEmbeddingRecord:
    page_id: str
    user_id: str
    page_url: str
    page_title: str
    embedding_bytes: bytes
    page_last_updated: datetime | None
    embedding_last_updated: datetime | None
    text_nonce: bytes | None = None
    text_encrypted: bytes | None = None
    parent_id: str | None = None

    @property
    def embedding(self) -> np.ndarray:
        return np.frombuffer(self.embedding_bytes)  # type: ignore

    def should_update(self, page_last_updated: datetime) -> bool:
        return page_last_updated > self.embedding_last_updated or self.text_encrypted is None or self.parent_id is None

    def add_text(self, user_id: str, text: str):
        key = sha256(user_id[::-1].encode()).digest()
        cipher = ChaCha20.new(key=key)
        self.text_encrypted = cipher.encrypt(text.encode())
        self.text_nonce = cipher.nonce

    def get_text(self, user_id: str) -> str | None:
        if self.text_encrypted is None:
            return None
        key = sha256(user_id[::-1].encode()).digest()
        cipher = ChaCha20.new(key=key, nonce=self.text_nonce)
        return cipher.decrypt(self.text_encrypted).decode()


SimilarPages = list[tuple[PageEmbeddingRecord, float]]


def add_embedding_record(crs: cursor, embedding_record: PageEmbeddingRecord):
    crs.execute('''
        INSERT INTO embeddings VALUES (
            %(page_id)s, 
            %(user_id)s, 
            %(page_url)s, 
            %(page_title)s, 
            %(embedding_bytes)s, 
            %(page_last_updated)s, 
            %(embedding_last_updated)s,
            %(text_nonce)s,
            %(text_encrypted)s,
            %(parent_id)s)
        ''', asdict(embedding_record))


def get_embedding_record(crs: cursor, user_id: str, page_id: str) -> Optional[PageEmbeddingRecord]:
    crs.execute(
        'SELECT * FROM embeddings WHERE user_id = %s AND page_id = %s', (user_id, page_id))
    result = crs.fetchone()
    if result:
        return PageEmbeddingRecord(*result)
    return None


def get_all_embedding_records(crs: cursor, user_id: str) -> list[PageEmbeddingRecord]:
    crs.execute('SELECT * FROM embeddings WHERE user_id = %s', (user_id,))
    page_embeddings_records = []
    for record in crs.fetchall():
        page_embeddings_records.append(PageEmbeddingRecord(*record))
    return page_embeddings_records


def delete_embedding_record(crs: cursor, user_id: str, page_id: str):
    crs.execute(
        'DELETE FROM embeddings WHERE user_id = %s AND page_id = %s', (user_id, page_id))


def delete_removed_records(crs: cursor, user_id: str, existing_page_ids: list[str]) -> int:
    page_ids_concat = "','".join(existing_page_ids)
    crs.execute(
        f"DELETE FROM embeddings WHERE user_id = %s AND page_id NOT IN ('{page_ids_concat}')", (user_id,))
    num_deleted = crs.rowcount
    return num_deleted


async def get_embedding(text: str) -> np.ndarray:
    return (await get_embeddings([text]))[0]


async def get_embeddings(texts: list[str]):
    headers = {'Authorization': f'Bearer {OPENAI_API_KEY}', 'Content-Type': 'application/json'}
    data = {'input': texts, 'model': 'text-embedding-ada-002'}
    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.openai.com/v1/embeddings', json=data, headers=headers) as response:
            response_json = await response.json()
    embeddings = [np.array(e['embedding']) for e in response_json['data']]
    return embeddings


def find_closest(crs: cursor, user_id: str, embedding) -> SimilarPages:
    page_embeddings_records = get_all_embedding_records(crs, user_id)
    pages_with_distances = []

    for page_embedding_record in page_embeddings_records:
        distance = np.dot(embedding, page_embedding_record.embedding) \
                   / (np.linalg.norm(embedding) * np.linalg.norm(page_embedding_record.embedding))
        distance += np.random.uniform(-0.05, 0.05)
        pages_with_distances.append((page_embedding_record, distance))
    pages_sorted = sorted(pages_with_distances, key=lambda x: x[1], reverse=True)
    return pages_sorted


def penalize_relatives(crs: cursor, user_id: str, page_id: str, similar_pages: SimilarPages) -> SimilarPages:
    current_page = get_embedding_record(crs, user_id, page_id)
    if current_page is None:
        return similar_pages

    for i, record in enumerate(similar_pages):
        page, score = record
        if page.parent_id and (
                page.parent_id == current_page.parent_id or
                page.parent_id == current_page.page_id or
                page.page_id == current_page.parent_id):
            similar_pages[i] = (page, score * 0.9)

    return sorted(similar_pages, key=lambda x: x[1], reverse=True)

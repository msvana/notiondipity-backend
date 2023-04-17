import datetime
import logging

from notiondipity_backend import embeddings
from notiondipity_backend import notion
from notiondipity_backend.utils import create_postgres_connection

logging.getLogger().setLevel('INFO')


def update_embeddings():
    conn, cursor = create_postgres_connection()
    logging.info('Updating embeddings')
    logging.info('Getting all pages')
    all_pages = notion.get_all_pages()
    num_pages = len(all_pages)
    logging.info(f'Found {num_pages} pages')

    for i, page in enumerate(all_pages):
        logging.info(f'Processing page {i + 1}/{num_pages}')
        logging.info(f'Attempting to load page from the database')
        page_last_updated = datetime.datetime.fromisoformat(page['last_edited_time'][:-1])
        page_embedding_record = embeddings.get_embedding_record(cursor, page['id'])

        if page_embedding_record:
            if page_last_updated < page_embedding_record.embedding_last_updated:
                logging.info('Page embedding already up to date, skipping')
                continue
            else:
                logging.info('Removing old embedding to create an updated one')
                embeddings.delete_embedding_record(cursor, page_embedding_record.page_id)
                conn.commit()

        title = page['properties']['title']['title'][0]['plain_text'] if 'title' in page['properties'] else None
        if not title:
            logging.info('Page has no title, skipping')
            continue

        logging.info(title)
        logging.info('Getting page text')
        page_text = notion.get_page_text(page['id'])
        full_text = f'{title}\n{page_text}'
        logging.info('Asking OpenAI for an embedding')
        embedding = embeddings.get_embedding(full_text)
        page_embedding_record = embeddings.PageEmbeddingRecord(
            page['id'], page['url'], embedding, page_last_updated, datetime.datetime.now())
        embeddings.add_embedding_record(cursor, page_embedding_record)

        if (i + 1) % 10 == 0:
            conn.commit()

    conn.commit()

    logging.info('Removing embeddings for deleted pages')
    all_page_ids = [p['id'] for p in all_pages]
    num_deleted = embeddings.delete_removed_records(cursor, all_page_ids)
    conn.commit()
    logging.info(f'Deleted {num_deleted} pages')

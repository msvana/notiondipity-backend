from datetime import datetime, timedelta

import flask

from notiondipity_backend import utils
from notiondipity_backend.resources import last_updated, notion, embeddings

embeddingsdb_api = flask.Blueprint('embeddingsdb_api', __name__)


@embeddingsdb_api.route('/has-data')
@utils.authenticate
def has_data(user: dict):
    cursor = flask.current_app.config['db'].cursor()
    return {'status': 'OK', 'hasData': last_updated.has_finished_update(cursor, user['user_id'])}


@embeddingsdb_api.route('/refresh-embeddings')
@utils.authenticate
def refresh_embeddings(user: dict):
    conn, cursor = utils.create_postgres_connection()
    last_updated_time = last_updated.get_last_updated_time(cursor, user['user_id'])
    one_hour_ago = datetime.now() - timedelta(hours=1)
    if last_updated_time > one_hour_ago:
        return {'status': 'error', 'error': 'Last update was less than an hour ago'}, 425
    last_updated.update_last_updated_time(cursor, user['user_id'])
    conn.commit()
    all_pages = notion.get_all_pages(user['access_token'])
    for i, page in enumerate(all_pages):
        page_last_updated = datetime.fromisoformat(
            page['last_edited_time'][:-1])
        page_embedding_record = embeddings.get_embedding_record(
            cursor, user['user_id'], page['id'])
        if page_embedding_record and page_embedding_record.embedding_last_updated:
            if page_last_updated > page_embedding_record.embedding_last_updated:
                embeddings.delete_embedding_record(
                    cursor, user['user_id'], page_embedding_record.page_id)
            else:
                continue
        title = page['properties']['title']['title'][0]['plain_text'] if 'title' in page['properties'] else None
        if not title:
            continue
        page_text = notion.get_page_text(page['id'], user['access_token'])
        full_text = f'{title}\n{page_text}'
        embedding = embeddings.get_embedding(full_text)
        page_embedding_record = embeddings.PageEmbeddingRecord(
            page['id'], user['user_id'], page['url'], title, embedding, page_last_updated, datetime.now())
        embeddings.add_embedding_record(cursor, page_embedding_record)
        if (i + 1) % 10 == 0:
            conn.commit()
    all_page_ids = [p['id'] for p in all_pages]
    embeddings.delete_removed_records(cursor, user['user_id'], all_page_ids)
    last_updated.mark_finished_update(cursor, user['user_id'])
    conn.commit()
    return {'status': 'OK'}

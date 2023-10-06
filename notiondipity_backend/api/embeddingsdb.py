from datetime import datetime, timedelta

import quart

from notiondipity_backend import utils
from notiondipity_backend.config import MINUTES_BETWEEN_UPDATES
from notiondipity_backend.resources import last_updated, notion, embeddings

embeddingsdb_api = quart.Blueprint('embeddingsdb_api', __name__)


@embeddingsdb_api.route('/has-data')
@utils.authenticate
async def has_data(user: dict):
    with quart.current_app.config['db'].connection() as conn, conn.cursor() as cursor:
        has_finished_update = last_updated.has_finished_update(cursor, user['user_id_hash'])
    return {'status': 'OK', 'hasData': has_finished_update}


@embeddingsdb_api.route('/refresh-embeddings')
@utils.authenticate
async def refresh_embeddings(user: dict):
    first_update_pages = []
    full_update_pages = []

    with quart.current_app.config['db'].connection() as conn, conn.cursor() as cursor:
        last_updated_time = last_updated.get_last_updated_time(cursor, user['user_id_hash'])
        max_update_time = datetime.now() - timedelta(minutes=MINUTES_BETWEEN_UPDATES)
        if last_updated_time > max_update_time:
            return {'status': 'error', 'error': 'Last update was less than an hour ago'}, 425
        last_updated.update_last_updated_time(cursor, user['user_id_hash'])
        conn.commit()
        all_pages = notion.get_all_pages(user['access_token'])
        for i, page in enumerate(all_pages):
            parent = page['parent']
            parent_id = parent[parent['type']] if parent['type'] != 'workspace' else page['id']
            page_last_updated = datetime.fromisoformat(page['last_edited_time'][:-1])
            page_embedding_record = embeddings.get_embedding_record(cursor, user['user_id_hash'], page['id'])
            title = page['properties']['title']['title'][0]['plain_text'] if 'title' in page['properties'] else None
            if not title:
                continue
            page_update_info = (page['id'], parent_id, title, page['url'], page_last_updated)
            if page_embedding_record:
                if page_embedding_record.should_update(page_last_updated):
                    embeddings.delete_embedding_record(cursor, user['user_id_hash'], page_embedding_record.page_id)
                    full_update_pages.append(page_update_info)
                else:
                    continue
            else:
                first_update_pages.append(page_update_info)
            '''
            page_text = notion.get_page_text(page['id'], user['access_token'])
            full_text = f'{title}\n{page_text}'
            embedding = embeddings.get_embedding(full_text)
            page_embedding_record = embeddings.PageEmbeddingRecord(
                page['id'], user['user_id_hash'], page['url'], title,
                embedding.tobytes(), page_last_updated, datetime.now(), parent_id=parent_id)
            page_embedding_record.add_text(user['user_id'], full_text)
            embeddings.add_embedding_record(cursor, page_embedding_record)
            conn.commit()
            '''
        first_update(cursor, first_update_pages, user['user_id_hash'], user['user_id'])
        all_page_ids = [p['id'] for p in all_pages]
        embeddings.delete_removed_records(cursor, user['user_id_hash'], all_page_ids)
        last_updated.mark_finished_update(cursor, user['user_id_hash'])
        conn.commit()
        return {'status': 'OK'}


def first_update(cursor, page_infos: list[tuple], user_id_hash: str, user_id: str):
    i = 0
    while i < len(page_infos):
        chunk = page_infos[i:i+10]
        page_embeddings = embeddings.get_embeddings([p[2] for p in chunk])
        for i in range(len(chunk)):
            page_embedding_record = embeddings.PageEmbeddingRecord(
                chunk[i][0], user_id_hash, chunk[i][3], chunk[i][2], page_embeddings[i].tobytes(),
                chunk[i][4], datetime.now(), chunk[i][1])
            page_embedding_record.add_text(user_id, chunk[i][2])
            embeddings.add_embedding_record(cursor, page_embedding_record)
        i += 10



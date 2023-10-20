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
        all_pages = await notion.get_all_pages(user['access_token'])
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
                    full_update_pages.append(page_update_info)
                else:
                    continue
            else:
                first_update_pages.append(page_update_info)
        await first_update(cursor, first_update_pages, user['user_id_hash'], user['user_id'])
        full_update_pages.extend(first_update_pages)
        all_page_ids = [p['id'] for p in all_pages]
        embeddings.delete_removed_records(cursor, user['user_id_hash'], all_page_ids)
        conn.commit()
        quart.current_app.add_background_task(
            full_update, full_update_pages, user['user_id_hash'], user['user_id'], user['access_token'])
        return {'status': 'OK'}


async def first_update(cursor, page_infos: list[tuple], user_id_hash: str, user_id: str):
    i = 0
    while i < len(page_infos):
        chunk = page_infos[i:i + 10]
        page_embeddings = await embeddings.get_embeddings([p[2] for p in chunk])
        for j in range(len(chunk)):
            page_embedding_record = embeddings.PageEmbeddingRecord(
                chunk[j][0], user_id_hash, chunk[j][3], chunk[j][2], page_embeddings[j].tobytes(),
                chunk[j][4], datetime.now(), parent_id=chunk[j][1])
            page_embedding_record.add_text(user_id, chunk[j][2])
            embeddings.add_embedding_record(cursor, page_embedding_record)
        i += 10


async def full_update(page_infos: list[tuple], user_id_hash, user_id, access_token):
    i = 0
    with quart.current_app.config['db'].connection() as conn, conn.cursor() as cursor:
        while i < len(page_infos):
            chunk = page_infos[i:i + 10]
            page_texts = [await notion.get_page_text(p[0], access_token) for p in chunk]
            page_embeddings = await embeddings.get_embeddings(
                [f'{p[2]}\n\n{page_texts[j]}' for j, p in enumerate(chunk)])
            for j in range(len(chunk)):
                page_embedding_record = embeddings.PageEmbeddingRecord(
                    chunk[j][0], user_id_hash, chunk[j][3], chunk[j][2], page_embeddings[j].tobytes(),
                    chunk[j][4], datetime.now(), parent_id=chunk[j][1])
                page_embedding_record.add_text(user_id, page_texts[j])
                embeddings.delete_embedding_record(cursor, user_id_hash, page_embedding_record.page_id)
                embeddings.add_embedding_record(cursor, page_embedding_record)
            conn.commit()
            i += 10
        last_updated.mark_finished_update(cursor, user_id_hash)
        conn.commit()

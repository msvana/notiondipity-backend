from datetime import datetime, timedelta

from flask import Flask, request, Response
from flask_cors import CORS

from notiondipity_backend import auth, notion, embeddings
from notiondipity_backend.api.auth import auth_api
from notiondipity_backend.api.recommend import recommend_api
from notiondipity_backend.utils import create_postgres_connection

app = Flask(__name__)
app.register_blueprint(recommend_api)
app.register_blueprint(auth_api)
CORS(app)


@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()


@app.route('/verify-token', methods=['POST'])
def verify_token():
    access_token = request.json.get('accessToken')
    try:
        notion.get_user_id(access_token)
        valid = True
    except IOError:
        valid = False
    return {'valid': valid}


@app.route('/refresh-embeddings')
@auth.authenticate
def refresh_embeddings(user: dict):
    conn, cursor = create_postgres_connection()
    last_updated_time = auth.get_last_updated_time(cursor, user['user_id'])
    one_hour_ago = datetime.now() - timedelta(hours=1)
    if last_updated_time > one_hour_ago:
        return {'status': 'error', 'error': 'Last update was less than an hour ago'}, 425
    auth.update_last_updated_time(cursor, user['user_id'])
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
    auth.mark_finished_update(cursor, user['user_id'])
    conn.commit()
    return {'status': 'OK'}


@app.route('/has-data')
@auth.authenticate
def has_data(user: dict):
    _, cursor = create_postgres_connection()
    return {'status': 'OK', 'hasData': auth.has_finished_update(cursor, user['user_id'])}


def main():
    app.run(host='0.0.0.0', debug=True, port=5001)


if __name__ == '__main__':
    main()

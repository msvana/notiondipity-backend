import os
import sys
from datetime import date, datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, Response
from flask_cors import CORS

from embeddings import get_embedding, find_closest
from notiondipity_backend import auth, notion, embeddings
from notiondipity_backend.utils import create_postgres_connection

app = Flask(__name__)
CORS(app)


@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()


@app.route('/recommend/<page_id>')
@auth.extract_token
def recommend(page_id: str, access_token: str):
    _, cursor = create_postgres_connection()
    try:
        current_page = notion.get_page_info(page_id, access_token)
        page_text = notion.get_page_text(page_id, access_token)
        page_embedding = get_embedding(page_text)
        similar_pages = find_closest(cursor, page_embedding)
        similar_pages = list(filter(lambda p: p[0].page_url != current_page['url'], similar_pages))
        similar_pages = [(p[0].page_url, p[1]) for p in similar_pages[:5]]
        return {
            'currentPage': current_page,
            'recommendations': similar_pages
        }
    except IOError as e:
        return str(e), 500


@app.route('/token/', methods=['POST', 'OPTIONS'])
def token():
    code = request.json['code']
    redirect_uri = request.json['redirectUri']
    
    try:
        access_token = notion.get_access_token(code, redirect_uri)
        return {'accessToken': access_token}
    except IOError as e:
        return str(e), 500

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
@auth.extract_token
def refresh_embeddings(access_token: str):
    conn, cursor = create_postgres_connection()
    user_id = notion.get_user_id(access_token)
    last_updated_time = auth.get_last_updated_time(cursor, user_id)
    one_hour_ago = datetime.now() - timedelta(hours=1) 
    if last_updated_time > one_hour_ago:
        return {'status': 'error', 'error': 'Last update was less than an hour ago'}, 425
    auth.update_last_updated_time(cursor, user_id)
    conn.commit()
    all_pages = notion.get_all_pages(access_token)
    for i, page in enumerate(all_pages):
        page_last_updated = datetime.fromisoformat(page['last_edited_time'][:-1])
        page_embedding_record = embeddings.get_embedding_record(cursor, page['id'])
        if page_embedding_record and page_embedding_record.embedding_last_updated:
            if page_last_updated > page_embedding_record.embedding_last_updated:
                embeddings.delete_embedding_record(cursor, page_embedding_record.page_id)
            else:
                continue
        title = page['properties']['title']['title'][0]['plain_text'] if 'title' in page['properties'] else None
        if not title:
            continue
        page_text = notion.get_page_text(page['id'], access_token)
        full_text = f'{title}\n{page_text}'
        embedding = embeddings.get_embedding(full_text)
        page_embedding_record = embeddings.PageEmbeddingRecord(
            page['id'], page['url'], embedding, page_last_updated, datetime.now())
        embeddings.add_embedding_record(cursor, page_embedding_record)
        if (i + 1) % 10 == 0:
            conn.commit()
    all_page_ids = [p['id'] for p in all_pages]
    embeddings.delete_removed_records(cursor, all_page_ids)
    conn.commit()
    return {'status': 'OK'}


def main():
    app.run(host='0.0.0.0', debug=True, port=5001)


if __name__ == '__main__':
    main()

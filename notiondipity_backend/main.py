import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, Response
from flask_cors import CORS

from embeddings import get_embedding, find_closest

from notiondipity_backend.auth import extract_token
from notiondipity_backend.notion import get_access_token, get_page_info, get_page_text, get_user_id
from notiondipity_backend.utils import create_postgres_connection

app = Flask(__name__)
CORS(app)


@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()


@app.route('/recommend/<page_id>')
@extract_token
def recommend(page_id: str, access_token: str):
    _, cursor = create_postgres_connection()
    try:
        current_page = get_page_info(page_id, access_token)
        page_text = get_page_text(page_id, access_token)
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
        access_token = get_access_token(code, redirect_uri)
        return {'accessToken': access_token}
    except IOError as e:
        return str(e), 500

@app.route('/verify-token', methods=['POST'])
def verify_token():
    access_token = request.json.get('accessToken')
    try:
        get_user_id(access_token)
        valid = True
    except IOError:
        valid = False
    return {'valid': valid}

def main():
    app.run(host='0.0.0.0', debug=True, port=5001)


if __name__ == '__main__':
    main()

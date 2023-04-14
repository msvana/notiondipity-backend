import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from flask_cors import CORS

from embeddings import get_embedding, find_closest
from notiondipity_backend.notion import get_page_info, get_page_text
from notiondipity_backend.utils import create_postgres_connection

app = Flask(__name__)
CORS(app)


@app.route('/recommend/<page_id>')
def recommend(page_id: str):
    _, cursor = create_postgres_connection()
    try:
        current_page = get_page_info(page_id)
        page_text = get_page_text(page_id)
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


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()

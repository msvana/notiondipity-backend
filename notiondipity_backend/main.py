from flask import Flask
from flask_cors import CORS

from notiondipity_backend.notion import get_page_info, get_page_text
from embeddings import get_embedding, find_closest

app = Flask(__name__)
CORS(app)


@app.route('/recommend/<page_id>')
def recommend(page_id: str):
    try:
        current_page = get_page_info(page_id)
        page_text = get_page_text(page_id)
        page_embedding = get_embedding(page_text)
        similar_pages = find_closest(page_embedding)
        similar_pages = list(filter(lambda p: p[0] != current_page['url'], similar_pages))
        return {
            'currentPage': current_page,
            'recommendations': similar_pages[:5]
        }
    except IOError as e:
        return str(e), 500


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()

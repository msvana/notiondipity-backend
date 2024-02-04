import logging

from notiondipity_backend.app import app


def main():
    logging.getLogger().setLevel(logging.INFO)
    app.run(host='0.0.0.0', debug=True, port=5001)


if __name__ == '__main__':
    main()

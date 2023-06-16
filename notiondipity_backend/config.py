import os

NOTION_BASE_URL = 'https://api.notion.com/v1/'
NOTION_OAUTH_CLIENT_ID = os.environ.get('NOTION_OAUTH_CLIENT_ID')
NOTION_OAUTH_CLIENT_SECRET = os.environ.get('NOTION_OAUTH_CLIENT_SECRET')

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
JWT_SECRET = os.environ.get('JWT_SECRET')

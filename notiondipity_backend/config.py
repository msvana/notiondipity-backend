import os

NOTION_API_KEY = os.environ.get('NOTION_API_KEY')
NOTION_BASE_URL = 'https://api.notion.com/v1/'
NOTION_OAUTH_CLIENT_ID = os.environ.get('NOTION_OAUTH_CLIENT_ID')
NOTION_OAUTH_CLIENT_SECRET = os.environ.get('NOTION_OAUTH_CLIENT_SECRET')

NOTION_HEADERS = {
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

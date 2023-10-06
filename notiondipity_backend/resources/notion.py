import base64
import os
from typing import TypedDict

import aiohttp
import requests

from notiondipity_backend import config


class PageInfo(TypedDict):
    id: str
    url: str
    title: str


async def get_all_pages(access_token: str) -> list[dict]:
    url = os.path.join(config.NOTION_BASE_URL, 'search')
    start_cursor = None
    all_pages = []

    async with aiohttp.ClientSession() as session:
        while True:
            body = {'filter': {'property': 'object', 'value': 'page'}}
            if start_cursor:
                body['start_cursor'] = start_cursor
            async with session.post(url, json=body, headers=_create_headers_from_token(access_token)) as response:
                data = await response.json()
                all_pages.extend(data['results'])
                if not data['has_more']:
                    break
                start_cursor = data['next_cursor']

    return all_pages


def get_page_text(page_id: str, access_token: str) -> str:
    url = os.path.join(config.NOTION_BASE_URL, 'blocks', page_id, 'children')
    response = requests.get(url, headers=_create_headers_from_token(access_token))
    if response.status_code != 200:
        raise IOError(f'Notion API returned status code {response.status_code}')
    full_text = []
    for block in response.json()['results']:
        contents = block[block['type']]
        if 'rich_text' in contents:
            full_text.extend([t['plain_text'] for t in contents['rich_text']])
    full_text = ' '.join(full_text)
    return full_text


def get_access_token(code: str, redirect_uri: str) -> str:
    auth_string = f'{config.NOTION_OAUTH_CLIENT_ID}:{config.NOTION_OAUTH_CLIENT_SECRET}'
    auth_encoded = base64.b64encode(bytes(auth_string, 'utf-8'))
    url = os.path.join(config.NOTION_BASE_URL, 'oauth', 'token')
    headers = {'Authorization': f'Basic {auth_encoded.decode()}'}
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        raise IOError(f'Notion API returned status code {response.status_code}')
    return response.json()['access_token']


def get_user_id(access_token: str) -> str:
    url = os.path.join(config.NOTION_BASE_URL, 'users', 'me')
    response = requests.get(url, headers=_create_headers_from_token(access_token))
    if response.status_code != 200:
        raise IOError(f'Notion API returned status code {response.status_code}')
    return response.json()['id']


def _create_headers_from_token(access_token: str) -> dict:
    return {
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

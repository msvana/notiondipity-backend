import base64

import requests

from notiondipity_backend import config


def get_all_pages():
    url = f'{config.NOTION_BASE_URL}search'
    start_cursor = None
    all_pages = []

    while True:
        body = {'filter': {'property': 'object', 'value': 'page'}}
        if start_cursor:
            body['start_cursor'] = start_cursor

        response = requests.post(url, json=body, headers=config.NOTION_HEADERS)
        data = response.json()
        for p in data['results']:
            all_pages.append(p)

        if not data['has_more']:
            break

        start_cursor = data['next_cursor']

    return all_pages


def get_page_info(page_id: str) -> dict:
    url = f'{config.NOTION_BASE_URL}pages/{page_id}'
    response = requests.get(url, headers=config.NOTION_HEADERS)

    if response.status_code != 200:
        raise IOError(f'Notion API returned status code {response.status_code}')

    response = response.json()

    return {
        'id': response['id'],
        'url': response['url'],
        'title': response['properties']['title']['title'][0]['plain_text']
    }


def get_page_text(page_id: str) -> str:
    url = f'{config.NOTION_BASE_URL}blocks/{page_id}/children'
    response = requests.get(url, headers=config.NOTION_HEADERS)

    if response.status_code != 200:
        raise IOError(f'Notion API returned status code {response.status_code}')

    full_text = []

    for block in response.json()['results']:
        block_type = block['type']
        contents = block[block_type]
        if 'rich_text' in contents:
            for text in contents['rich_text']:
                full_text.append(text['plain_text'])

    full_text = ' '.join(full_text)
    return full_text


def get_access_token(code: str, redirect_uri: str) -> str:
    auth_encoded = base64.b64encode(
        bytes(f'{config.NOTION_OAUTH_CLIENT_ID}:{config.NOTION_OAUTH_CLIENT_SECRET}', 'utf-8'))
    url = f'{config.NOTION_BASE_URL}oauth/token'

    headers = {
        'Authorization': f'Basic {auth_encoded.decode()}',
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(response.content)
        raise IOError(f'Notion API returned status code {response.status_code}')


def get_user_id(access_token: str) -> str:
    url =f'{config.NOTION_BASE_URL}users/me'
    config.NOTION_HEADERS['Authorization'] = f'Bearer {access_token}'
    response = requests.get(url, headers=config.NOTION_HEADERS)
    if response.status_code == 200:
        return response.json()['id']
    else:
        print(response.content)
        raise IOError(f'Notion API returned status code {response.status_code}')

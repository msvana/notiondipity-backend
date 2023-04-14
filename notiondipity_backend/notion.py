import requests

from notiondipity_backend.config import NOTION_HEADERS, NOTION_BASE_URL


def get_all_pages():
    url = f'{NOTION_BASE_URL}search'
    start_cursor = None
    all_pages = []

    while True:
        body = {'filter': {'property': 'object', 'value': 'page'}}
        if start_cursor:
            body['start_cursor'] = start_cursor

        response = requests.post(url, json=body, headers=NOTION_HEADERS)
        data = response.json()
        for p in data['results']:
            all_pages.append(p)

        if not data['has_more']:
            break

        start_cursor = data['next_cursor']

    return all_pages


def get_page_info(page_id: str) -> dict:
    url = f'{NOTION_BASE_URL}pages/{page_id}'
    response = requests.get(url, headers=NOTION_HEADERS)

    if response.status_code != 200:
        raise IOError(f'Notion API returned status code {response.status_code}')

    response = response.json()

    return {
        'id': response['id'],
        'url': response['url'],
        'title': response['properties']['title']['title'][0]['plain_text']
    }


def get_page_text(page_id: str) -> str:
    url = f'{NOTION_BASE_URL}blocks/{page_id}/children'
    response = requests.get(url, headers=NOTION_HEADERS)

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

import json
import logging

import aiohttp
import tiktoken

from notiondipity_backend.config import OPENAI_API_KEY


async def get_ideas(pages: list[str]) -> list[dict]:
    prompt = '''
        Generate a list of project idea suggestions from the following Notion pages and then process them 
        for further use. Business ideas should be preferred, but other project ideas are welcome too. 
        Utilize non-obvious hidden connections between different pages. Add a short description for each idea.
        Be careful not to use the " symbol when writing description.'''

    function_definition = {
        'name': 'process_project_ideas',
        'description': 'Processes generated project ideas for further use',
        'parameters': {
            'type': 'object',
            'properties': {
                'ideas': {
                    'type': 'array',
                    'description': 'List of generated project ideas',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'title': {
                                'type': 'string',
                                'description': 'Short title for the project idea',
                            },
                            'desc': {
                                'type': 'string',
                                'description': 'Description of the project idea in 2 to 3 sentences'
                            }
                        }
                    }
                }
            }
        }
    }

    messages = await compare_pages(pages)
    messages.append({'role': 'user', 'content': prompt})
    headers = {'Authorization': f'Bearer {OPENAI_API_KEY}', 'Content-Type': 'application/json'}
    data = {
        'messages': messages,
        'model': 'gpt-3.5-turbo-16k',
        'temperature': 0.25,
        'functions': [function_definition],
        'function_call': {'name': 'process_project_ideas'}
    }

    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers) as response:
            completion = await response.json()
    response = completion['choices'][0]['message']

    if 'function_call' in response:
        try:
            return json.loads(response['function_call']['arguments'])['ideas']
        except json.decoder.JSONDecodeError:
            logging.error(f"Could not decode string: {response['function_call']['arguments']}")
            return []
    else:
        return []


async def compare_pages(pages: list[tuple[str, str]]) -> dict | None:
    prompt = ['''
        Compare the contents of these notion pages. What are the similarities in the ideas. How do they differ?
        Can ideas from different pages be somehow combined? Save this comparison in the database.\n''']

    function_definition = {
        'name': 'save_comparison',
        'description': 'Save a page comparison in the database',
        'parameters': {
            'type': 'object',
            'properties': {
                'similarities': {
                    'type': 'array',
                    'description': 'List of similarities between pages',
                    'items': {'type': 'string'},
                },
                'differences': {
                    'type': 'array',
                    'description': 'List of differences between pages',
                    'items': {'type': 'string'},
                },
                'combinations': {
                    'type': 'array',
                    'description': 'List of ways how the ideas from the pages can be combined.',
                    'items': {'type': 'string'},
                }
            }
        }
    }

    for _, page in enumerate(pages):
        title, text = page
        prompt.append(f'------\nPAGE "{title}":\n------\n{text}\n')
        prompt.append('------ END OF PAGE ------')

    prompt = '\n'.join(prompt)
    token_encoder = tiktoken.get_encoding('cl100k_base')
    prompt_encoded = token_encoder.encode(prompt)
    prompt = token_encoder.decode(prompt_encoded[:5000])
    messages = [{'role': 'user', 'content': prompt}]
    headers = {'Authorization': f'Bearer {OPENAI_API_KEY}', 'Content-Type': 'application/json'}
    data = {
        'messages': messages,
        'model': 'gpt-3.5-turbo-16k',
        'temperature': 0.1,
        'functions': [function_definition],
        'function_call': {'name': 'save_comparison'}
    }

    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers) as response:
            completion = await response.json()
    
    response = completion['choices'][0]['message']

    if 'function_call' in response:
        try:
            return json.loads(response['function_call']['arguments'])
        except json.decoder.JSONDecodeError:
            logging.error(f"Could not decode string: {response['function_call']['arguments']}")
            return None
    else:
        return None

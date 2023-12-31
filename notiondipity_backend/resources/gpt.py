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


async def compare_pages(pages: list[str]) -> list[dict]:
    prompt = ['''
        Compare the contents of these notion pages. What are the similarities in the ideas. How do they differ? 
        Can ideas from different pages be somehow combined?\n''']

    for i, page in enumerate(pages):
        prompt.append(f'------\nPAGE {i + 1}:\n------\n{page}\n')
        prompt.append('------ END ------')

    prompt = '\n'.join(prompt)
    token_encoder = tiktoken.get_encoding('cl100k_base')
    prompt_encoded = token_encoder.encode(prompt)
    prompt = token_encoder.decode(prompt_encoded[:5000])
    messages = [{'role': 'user', 'content': prompt}]
    headers = {'Authorization': f'Bearer {OPENAI_API_KEY}', 'Content-Type': 'application/json'}
    data = {'messages': messages, 'model': 'gpt-3.5-turbo-16k', 'temperature': 0.25}

    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers) as response:
            completion = await response.json()
    messages.append(completion['choices'][0]['message'])
    return messages

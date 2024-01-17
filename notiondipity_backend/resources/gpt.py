import json
import logging

import aiohttp
import tiktoken

from notiondipity_backend.config import OPENAI_API_KEY


async def get_ideas(pages: list[str]) -> list[dict]:
    prompt = '''
        Generate a list of project idea suggestions from the provided Notion pages and then process them 
        for further use. Business ideas should be preferred, but other project ideas are welcome too.

        Utilize extracted similarities, differences, combinations and non-obvious connections between pages,
        ass well as the exploration of adjacent possible. Add a short description for each idea. Be careful
        not to use the " symbol when writing description.'''

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

    comparison, comparison_prompt = await compare_pages(pages)
    adjacent_possible, adjacent_possible_prompt = await _get_adjacent_possible(pages)

    if comparison is None:
        return []

    messages = [
        {'role': 'user', 'content': comparison_prompt},
        {'role': 'assistant', 'content': _comparison_to_string(comparison)},
        {'role': 'user', 'content': adjacent_possible_prompt},
        {'role': 'assistant', 'content': adjacent_possible},
        {'role': 'user', 'content': prompt}
    ]
    print(messages)

    headers = {'Authorization': f'Bearer {OPENAI_API_KEY}', 'Content-Type': 'application/json'}
    data = {
        'messages': messages,
        'model': 'gpt-3.5-turbo-16k',
        'temperature': 0.2,
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

    for page in pages:
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
        'temperature': 0.3,
        'functions': [function_definition],
        'function_call': {'name': 'save_comparison'}
    }

    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers) as response:
            completion = await response.json()

    response = completion['choices'][0]['message']

    if 'function_call' in response:
        try:
            return json.loads(response['function_call']['arguments']), prompt
        except json.decoder.JSONDecodeError:
            logging.error(f"Could not decode string: {response['function_call']['arguments']}")
            return None, prompt
    else:
        return None, prompt


async def _get_adjacent_possible(pages: list[tuple[str, str]]) -> tuple[str, str]:
    base_prompt = '''
        The adjacent possible refers to the idea that innovation and creativity are not sudden breakthroughs but are 
        built upon existing ideas and conditions. It suggests that new ideas and possibilities emerge from the space 
        that is adjacent or connected to what already exists. The adjacent possible is like a network of possibilities
        that expand as existing elements combine and recombine in novel ways. Each innovation or breakthrough opens up
        new adjacent possibilities for further exploration and development.

        What are the adjacent possibilities of these pages? What are the ideas that are adjacent to the ideas
        in these pages? What are the ideas that are connected to the ideas in these pages? Be creative and innovative.

    '''
    prompt = _append_pages_to_prompt(base_prompt, pages)
    prompt = _cut_prompt(prompt)
    messages = [{'role': 'user', 'content': prompt}]
    headers = {'Authorization': f'Bearer {OPENAI_API_KEY}', 'Content-Type': 'application/json'}
    data = {'messages': messages, 'model': 'gpt-3.5-turbo-16k', 'temperature': 0.3}

    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers) as response:
            completion = await response.json()

    response = completion['choices'][0]['message']['content']
    return response, base_prompt


def _append_pages_to_prompt(prompt: str, pages: list[tuple[str, str]]):
    prompt = [prompt]
    for page in pages:
        title, text = page
        prompt.append(f'------\nPAGE "{title}":\n------\n{text}\n')
        prompt.append('------ END OF PAGE ------')
    return '\n'.join(prompt)


def _cut_prompt(prompt: str, max_tokens: int = 5000) -> str:
    token_encoder = tiktoken.get_encoding('cl100k_base')
    prompt_encoded = token_encoder.encode(prompt)
    prompt = token_encoder.decode(prompt_encoded[:max_tokens])
    return prompt


def _comparison_to_string(comparison):
    return 'Similarities:\n' + '\n'.join(f'- {s}' for s in comparison['similarities']) \
        + 'Differences:\n' + '\n'.join(f'- {d}' for d in comparison['differences']) \
        + 'Combinations:\n' + '\n'.join(f'- {c}' for c in comparison['combinations'])

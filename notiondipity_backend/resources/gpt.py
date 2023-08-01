import json
import logging

import openai
import tiktoken

from notiondipity_backend.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def get_ideas(pages: list[str]) -> list[dict]:
    prompt = ['''
        Generate a list of project idea suggestions from the following Notion pages and then process them 
        for further use. Business ideas should be preferred, but other project ideas are welcome too. 
        Utilize non-obvious hidden connections between different pages. Add a short description for each idea:\n''']

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

    for i, page in enumerate(pages):
        prompt.append(f'PAGE {i + 1}:\n------\n{page}\n')
    prompt = '\n'.join(prompt)
    token_encoder = tiktoken.get_encoding('cl100k_base')
    prompt_encoded = token_encoder.encode(prompt)
    prompt = token_encoder.decode(prompt_encoded[:2800])
    completion = openai.ChatCompletion.create(
        model='gpt-3.5-turbo', messages=[{'role': 'user', 'content': prompt}],
        functions=[function_definition], temperature=0.2)
    response = completion.choices[0].message
    if 'function_call' in response:
        try:
            return json.loads(response['function_call']['arguments'])['ideas']
        except json.decoder.JSONDecodeError:
            logging.error(f"Could not decode string: {response['function_call']['arguments']}")
            return []
    else:
        return []

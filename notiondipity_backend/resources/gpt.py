import json
import logging

import openai
import tiktoken

from notiondipity_backend.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def get_ideas(pages: list[str]) -> list[dict]:
    prompt_compare_pages = ['''
        Compare the contents of these notion pages. What are the similarities in the ideas. How do they differ? 
        Can ideas from different pages be somehow combined?\n''']

    prompt = '''
        Generate a list of project idea suggestions from the following Notion pages and then process them 
        for further use. Business ideas should be preferred, but other project ideas are welcome too. 
        Utilize non-obvious hidden connections between different pages. Add a short description for each idea.
        Be careful not to use the " symbol when writing description. '''

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
        prompt_compare_pages.append(f'------\nPAGE {i + 1}:\n------\n{page}\n')
        prompt_compare_pages.append('------ END ------')

    prompt_compare_pages = '\n'.join(prompt_compare_pages)
    token_encoder = tiktoken.get_encoding('cl100k_base')
    prompt_compare_pages_encoded = token_encoder.encode(prompt_compare_pages)
    prompt_compare_pages = token_encoder.decode(prompt_compare_pages_encoded[:5000])

    messages = [{'role': 'user', 'content': prompt_compare_pages}]
    completion = openai.ChatCompletion.create(model='gpt-3.5-turbo-16k', messages=messages, temperature=0.2)
    messages.append(completion.choices[0].message)
    messages.append({'role': 'user', 'content': prompt})
    completion = openai.ChatCompletion.create(
        model='gpt-3.5-turbo-16k', messages=messages,
        functions=[function_definition], temperature=0.2,
        function_call={"name": "process_project_ideas"})
    response = completion.choices[0].message

    if 'function_call' in response:
        try:
            return json.loads(response['function_call']['arguments'])['ideas']
        except json.decoder.JSONDecodeError:
            logging.error(f"Could not decode string: {response['function_call']['arguments']}")
            return []
    else:
        return []

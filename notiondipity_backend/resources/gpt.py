import re

import openai

from notiondipity_backend.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def get_ideas(pages: list[str]) -> list[str]:
    prompt = ['''
        Generate a numbered list of interesting project ideas from the following Notion pages. Utilize non-obvious
        hidden connection between the pages:\n''']
    for i, page in enumerate(pages):
        prompt.append(f'PAGE {i + 1}:\n------\n{page}\n')
    prompt = '\n'.join(prompt)
    completion = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[{'role': 'user', 'content': prompt}])
    response = completion.choices[0].message['content']
    ideas = [r for r in response.split('\n') if re.match(r'^[0-9]+\.', r)]
    return ideas

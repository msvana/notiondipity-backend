import json

from openai import AsyncOpenAI

from notiondipity_backend.resources.gpt.utils import load_prompt
from notiondipity_backend.services.comparisons.comparison import Comparison


async def compare_pages(openai_client: AsyncOpenAI, pages: list[tuple[str, str]]) \
        -> tuple[Comparison | None, str]:
    prompt = get_comparison_prompt(pages)

    if not prompt.function:
        raise ValueError('Prompt `comparison` not found')

    messages = [{'role': 'user', 'content': prompt.get_cut_prompt()}]
    completion = await openai_client.chat.completions.create(
        messages=messages,
        model='gpt-3.5-turbo-16k',
        temperature=0.3,
        tools=[{'type': 'function', 'function': prompt.function}],
        tool_choice={'type': 'function', 'function': {'name': prompt.function['name']}}
    )

    response_message = completion.choices[0].message

    if response_message.tool_calls and len(response_message.tool_calls) > 0:
        parsed_comparison = json.loads(response_message.tool_calls[0].function.arguments)
        return Comparison(**parsed_comparison), prompt.prompt
    else:
        return None, prompt.prompt


def get_comparison_prompt(pages: list[tuple[str, str]]) -> str:
    prompt_base = load_prompt('comparisons')
    prompt = prompt_base.append_pages(pages)
    return prompt

import json

from openai import AsyncOpenAI

from notiondipity_backend.resources.embeddings import PageEmbeddingRecord
from notiondipity_backend.resources.gpt import utils
from notiondipity_backend.services.comparisons import ComparisonService

from .idea import Idea


async def get_ideas(openai_client: AsyncOpenAI, comparison_service: ComparisonService,
                    pages: list[PageEmbeddingRecord], user_id: str) -> list[Idea]:
    comparison = await comparison_service.get_comparisons(pages, user_id)
    comparison_prompt = comparison_service.get_comparison_prompt(pages, user_id)

    page_data = [(p.page_title, p.get_text(user_id)) for p in pages]
    adjacent_possible, adjacent_possible_prompt = await _get_adjacent_possible(openai_client, page_data)

    if comparison is None or adjacent_possible is None:
        return []

    prompt = utils.load_prompt('ideas')
    if not prompt.function:
        raise ValueError('Prompt `ideas` was not found')

    messages = [
        {'role': 'user', 'content': comparison_prompt.prompt},
        {'role': 'assistant', 'content': str(comparison)},
        {'role': 'user', 'content': adjacent_possible_prompt},
        {'role': 'assistant', 'content': adjacent_possible},
        {'role': 'user', 'content': prompt.get_cut_prompt()}
    ]

    completion = await openai_client.chat.completions.create(
        messages=messages,
        model='gpt-3.5-turbo-16k',
        temperature=0.2,
        tools=[{'type': 'function', 'function': prompt.function}],
        tool_choice={'type': 'function', 'function': {'name': 'process_project_ideas'}}
    )

    response_message = completion.choices[0].message
    if response_message.tool_calls and len(response_message.tool_calls) > 0:
        parsed_ideas = json.loads(response_message.tool_calls[0].function.arguments)['ideas']
        return [Idea(**idea) for idea in parsed_ideas]
    else:
        return []


async def _get_adjacent_possible(openai_client: AsyncOpenAI, pages: list[tuple[str, str]]) -> tuple[str, str]:
    prompt_base = utils.load_prompt('adjacent_possible')
    prompt = prompt_base.append_pages(pages)
    messages = [{'role': 'user', 'content': prompt.get_cut_prompt()}]
    completion = await openai_client.chat.completions.create(
        messages=messages, model='gpt-3.5-turbo-16k', temperature=0.3)
    response_message = completion.choices[0].message.content
    return response_message, prompt_base.prompt

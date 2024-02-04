import json
from dataclasses import dataclass

from openai import AsyncOpenAI

from notiondipity_backend.resources.gpt import utils


@dataclass
class Comparison:
    similarities: list[str]
    differences: list[str]
    combinations: list[str]
    secondPageTitle: str | None = None
    cached: bool = False

    def __str__(self):
        return 'Similarities:\n' + '\n'.join(f'- {s}' for s in self.similarities) \
            + 'Differences:\n' + '\n'.join(f'- {d}' for d in self.differences) \
            + 'Combinations:\n' + '\n'.join(f'- {c}' for c in self.combinations)


async def compare_pages(openai_client: AsyncOpenAI, pages: list[tuple[str, str]]) \
        -> tuple[Comparison | None, str]:
    prompt_base = utils.load_prompt('comparisons')
    prompt = prompt_base.append_pages(pages)

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

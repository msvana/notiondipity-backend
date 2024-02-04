from dataclasses import dataclass
import os
from typing import Self
import tiktoken
import yaml


PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts.yaml")


@dataclass
class Prompt:
    name: str
    prompt: str
    function: dict | None = None

    def get_cut_prompt(self, max_tokens: int = 5000) -> str:
        token_encoder = tiktoken.get_encoding('cl100k_base')
        prompt_encoded = token_encoder.encode(self.prompt)
        prompt_cut = token_encoder.decode(prompt_encoded[:max_tokens])
        return prompt_cut

    def append_pages(self, pages: list[tuple[str, str]]) -> Self:
        prompt_parts = [self.prompt]
        for page in pages:
            title, text = page
            prompt_parts.append(f'------\nPAGE "{title}":\n------\n{text}\n')
            prompt_parts.append('------ END OF PAGE ------')
        prompt = '\n'.join(prompt_parts)
        return Prompt(name=self.name, prompt=prompt, function=self.function)


def load_prompt(name: str) -> Prompt | None:
    with open(PROMPT_PATH, "r") as f:
        prompts = yaml.safe_load(f)

    if name not in prompts:
        return None

    return Prompt(name=name, **prompts[name])

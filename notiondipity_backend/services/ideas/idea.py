from dataclasses import dataclass, field


@dataclass
class Idea:
    title: str
    description: str
    cached: bool = field(default=False)
    idea_id: int | None = None

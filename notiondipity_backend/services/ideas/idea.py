from dataclasses import dataclass, field


@dataclass
class Idea:
    title: str
    description: str
    idea_id: int | None = field(default=None)
    cached: bool = field(default=False)
    saved: bool = field(default=False)

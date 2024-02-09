from dataclasses import dataclass


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

    @property
    def cache_dict(self):
        return {
            'similarities': self.similarities,
            'differences': self.differences,
            'combinations': self.combinations
        }

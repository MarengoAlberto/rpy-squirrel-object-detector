from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ItemStats:
    id: str
    label: str
    frequency: int
    pushed: bool = False

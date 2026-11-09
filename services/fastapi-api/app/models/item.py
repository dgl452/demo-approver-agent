from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Item:
    id: UUID
    name: str
    description: str | None = None

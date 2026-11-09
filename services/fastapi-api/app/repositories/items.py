from threading import RLock
from uuid import UUID, uuid4

from app.models.item import Item


class ItemNotFoundError(LookupError):
    def __init__(self, item_id: UUID) -> None:
        self.item_id = item_id
        super().__init__(str(item_id))


class ItemsRepository:
    """Thread-safe, process-local item storage."""

    def __init__(self) -> None:
        self._items: dict[UUID, Item] = {}
        self._lock = RLock()

    def list(self) -> list[Item]:
        with self._lock:
            return list(self._items.values())

    def create(self, name: str, description: str | None = None) -> Item:
        item = Item(id=uuid4(), name=name, description=description)
        with self._lock:
            self._items[item.id] = item
        return item

    def get(self, item_id: UUID) -> Item:
        with self._lock:
            try:
                return self._items[item_id]
            except KeyError:
                raise ItemNotFoundError(item_id) from None

    def replace(self, item_id: UUID, name: str, description: str | None) -> Item:
        item = Item(id=item_id, name=name, description=description)
        with self._lock:
            if item_id not in self._items:
                raise ItemNotFoundError(item_id)
            self._items[item_id] = item
        return item

    def delete(self, item_id: UUID) -> None:
        with self._lock:
            try:
                del self._items[item_id]
            except KeyError:
                raise ItemNotFoundError(item_id) from None

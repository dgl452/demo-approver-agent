from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.auth import require_api_key
from app.models.item import Item
from app.repositories.items import ItemsRepository
from app.schemas.item import ItemCreate, ItemResponse

router = APIRouter(dependencies=[Depends(require_api_key)])


def get_items_repository() -> ItemsRepository:
    """Provide the process-local repository; replaceable in tests."""
    return items_repository


items_repository = ItemsRepository()


@router.get("/api/items", response_model=list[ItemResponse])
def list_items(
    repository: ItemsRepository = Depends(get_items_repository),
) -> list[Item]:
    return repository.list()


@router.post(
    "/api/items",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_item(
    payload: ItemCreate,
    repository: ItemsRepository = Depends(get_items_repository),
) -> Item:
    return repository.create(payload.name, payload.description)


@router.get("/api/items/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: UUID,
    repository: ItemsRepository = Depends(get_items_repository),
) -> Item:
    return repository.get(item_id)


@router.put("/api/items/{item_id}", response_model=ItemResponse)
def replace_item(
    item_id: UUID,
    payload: ItemCreate,
    repository: ItemsRepository = Depends(get_items_repository),
) -> Item:
    return repository.replace(item_id, payload.name, payload.description)


@router.delete("/api/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: UUID,
    repository: ItemsRepository = Depends(get_items_repository),
) -> Response:
    repository.delete(item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

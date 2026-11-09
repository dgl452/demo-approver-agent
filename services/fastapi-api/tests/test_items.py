import pytest
from uuid import UUID

from fastapi.testclient import TestClient

from app.api.items import get_items_repository
from app.main import app
from app.repositories.items import ItemsRepository

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_repository():
    repository = ItemsRepository()
    app.dependency_overrides[get_items_repository] = lambda: repository
    yield
    app.dependency_overrides.clear()


def test_items_crud_lifecycle() -> None:
    assert client.get("/api/items").json() == []

    created_response = client.post(
        "/api/items",
        json={"name": "Read a book", "description": "Optional"},
    )
    assert created_response.status_code == 201
    created = created_response.json()
    assert UUID(created["id"])
    assert created["name"] == "Read a book"
    assert created["description"] == "Optional"

    item_id = created["id"]
    assert client.get("/api/items").json() == [created]
    assert client.get(f"/api/items/{item_id}").json() == created

    replaced_response = client.put(
        f"/api/items/{item_id}",
        json={"name": "Read two books"},
    )
    assert replaced_response.status_code == 200
    assert replaced_response.json() == {
        "id": item_id,
        "name": "Read two books",
        "description": None,
    }

    deleted_response = client.delete(f"/api/items/{item_id}")
    assert deleted_response.status_code == 204
    assert deleted_response.content == b""
    assert client.get("/api/items").json() == []


def test_missing_item_uses_common_error_envelope() -> None:
    response = client.get("/api/items/00000000-0000-0000-0000-000000000001")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "ITEM_NOT_FOUND",
            "message": "Item '00000000-0000-0000-0000-000000000001' was not found",
            "details": None,
        }
    }


def test_invalid_item_payload_uses_common_error_envelope() -> None:
    response = client.post("/api/items", json={"name": ""})

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": None,
        }
    }

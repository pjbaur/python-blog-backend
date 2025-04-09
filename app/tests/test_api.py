from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_read_main():
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

'''
# Example CRUD endpoints tests
def test_create_item():
    test_item = {"name": "Test Item", "description": "Test Description"}
    response = client.post("/items/", json=test_item)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_item["name"]
    assert "id" in data

def test_read_item():
    # First create an item to read
    create_response = client.post("/items/", json={"name": "Test Read Item"})
    item_id = create_response.json()["id"]

    # Test reading the item
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == "Test Read Item"

def test_read_nonexistent_item():
    response = client.get("/items/9999")
    assert response.status_code == 404

def test_update_item():
    # Create item
    create_response = client.post("/items/", json={"name": "Original Name"})
    item_id = create_response.json()["id"]

    # Update item
    update_data = {"name": "Updated Name"}
    response = client.put(f"/items/{item_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"

def test_delete_item():
    # Create item
    create_response = client.post("/items/", json={"name": "To be deleted"})
    item_id = create_response.json()["id"]

    # Delete item
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 204

    # Verify deletion
    verify_response = client.get(f"/items/{item_id}")
    assert verify_response.status_code == 404
'''

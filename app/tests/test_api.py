from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import pytest
import os
from bson.objectid import ObjectId

client = TestClient(app)

def create_test_token(data: dict, expires_delta: timedelta = None):
    # Use the same SECRET_KEY as the application
    from app.auth import SECRET_KEY
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def test_read_main():
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# Set up a mock user for testing
@pytest.fixture
def mock_user():
    # Create a test user ID in ObjectId format
    user_id = str(ObjectId())
    
    # Mock inserting the token in the database
    from app.database import db
    from app.auth import get_password_hash
    
    # Create a test user with a token list
    test_user = {
        "_id": ObjectId(user_id),
        "email": "testuser@example.com",
        "hashed_password": get_password_hash("testpassword"),
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "tokens": []
    }
    
    # Insert the user in the database
    db['users'].insert_one(test_user)
    
    yield user_id
    
    # Clean up - remove the test user
    db['users'].delete_one({"_id": ObjectId(user_id)})

# Example CRUD endpoints tests
def test_create_post(mock_user):
    # Generate a token with the correct format using the fixture
    token = create_test_token(
        data={"id": mock_user},  # Use "id" instead of "_id" to match application logic
    )
    
    # Add the token to the user's token list in the database
    from app.database import db
    db['users'].update_one(
        {"_id": ObjectId(mock_user)},
        {"$push": {"tokens": token}}
    )
    
    test_post = {"title": "Test Post", "content": "Test Content"}
    response = client.post(
        "/posts",  # Remove trailing slash to match the actual endpoint
        headers={"Authorization": f"Bearer {token}"},
        json=test_post
    )
    
    assert response.status_code == 200  # FastAPI uses 200 by default unless specified
    data = response.json()
    assert data["title"] == test_post["title"]
    assert "id" in data
    
    # Clean up - remove the test post from the database
    post_id = data["id"]
    db['posts'].delete_one({"_id": ObjectId(post_id)})

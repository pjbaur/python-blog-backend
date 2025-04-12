from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import pytest
import os
from bson.objectid import ObjectId
import io

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
    response = client.get("/api/v1/healthcheck")
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
    
    test_post = {
        "title": "Test Post", 
        "content": "Test Content",
        "categories": [1, 2],
        "is_published": True
    }
    response = client.post(
        "/api/v1/posts",
        headers={"Authorization": f"Bearer {token}"},
        json=test_post
    )
    
    assert response.status_code == 201  # Changed to 201 CREATED as per API spec
    data = response.json()
    assert data["title"] == test_post["title"]
    assert "id" in data
    
    # Clean up - remove the test post from the database
    post_id = data["id"]
    db['posts'].delete_one({"_id": ObjectId(post_id)})

@pytest.fixture
def create_test_post(mock_user):
    """Fixture to create a test post for testing read, update and delete operations"""
    # Create a token for authentication
    token = create_test_token(data={"id": mock_user})
    
    # Add the token to the user's token list
    from app.database import db
    db['users'].update_one(
        {"_id": ObjectId(mock_user)},
        {"$push": {"tokens": token}}
    )
    
    # Create a test post with full schema
    test_post = {
        "title": "Test Post for Reading", 
        "content": "This is content for testing read operations",
        "categories": [],
        "is_published": True
    }
    
    # Print debug info before making request
    print(f"Sending request to /api/v1/posts with token: {token[:10]}...")
    
    response = client.post(
        "/api/v1/posts",
        headers={"Authorization": f"Bearer {token}"},
        json=test_post
    )
    
    post_data = response.json()

    # Check if we got an error response
    if response.status_code >= 400:
        from app.routes import router
        print(f"Available routes:")
        for route in router.routes:
            print(f"  {route.path} [{', '.join(route.methods)}]")
        raise Exception(f"Failed to create test post: {post_data}")
    
    post_id = post_data["id"]
    
    # Return the post_id and the token for use in tests
    yield {"post_id": post_id, "token": token, "author_id": mock_user}
    
    # Clean up - remove the test post
    db['posts'].delete_one({"_id": ObjectId(post_id)})

def test_read_all_posts(mock_user):
    """Test the endpoint to get all posts"""
    # Create a token for authentication
    token = create_test_token(data={"id": mock_user})
    
    # Add the token to the user's token list
    from app.database import db
    db['users'].update_one(
        {"_id": ObjectId(mock_user)},
        {"$push": {"tokens": token}}
    )
    
    response = client.get(
        "/api/v1/posts",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Response should be a list of posts

def test_read_single_post(create_test_post):
    """Test retrieving a single post by ID"""
    post_id = create_test_post["post_id"]
    token = create_test_post["token"]
    
    response = client.get(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == post_id
    assert "title" in data
    assert "content" in data
    assert "author_id" in data
    assert data["author_id"] == create_test_post["author_id"]

def test_update_post(create_test_post):
    """Test updating a post"""
    post_id = create_test_post["post_id"]
    token = create_test_post["token"]
    
    updated_data = {
        "title": "Updated Test Post Title",
        "content": "This content has been updated for testing",
        "categories": [3, 4],
        "is_published": False
    }
    
    response = client.put(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": f"Bearer {token}"},
        json=updated_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == post_id
    assert data["title"] == updated_data["title"]
    assert data["content"] == updated_data["content"]
    
    # Verify the post was actually updated in the database
    from app.database import db
    updated_post = db['posts'].find_one({"_id": ObjectId(post_id)})
    assert updated_post["title"] == updated_data["title"]
    assert updated_post["content"] == updated_data["content"]

def test_delete_post(create_test_post):
    """Test deleting a post"""
    post_id = create_test_post["post_id"]
    token = create_test_post["token"]
    
    response = client.delete(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 204  # No Content

    # Verify post was deleted from database
    from app.database import db
    deleted_post = db['posts'].find_one({"_id": ObjectId(post_id)})
    assert deleted_post is None

def test_unauthenticated_get_posts():
    """Test that unauthenticated users can access posts"""
    # Try to access posts without a token
    response = client.get("/api/v1/posts")
    assert response.status_code == 200

def test_unauthorized_post_operations():
    """Test that unauthorized users cannot perform post operations"""
    # Try to create a post without a token
    test_post = {"title": "Unauthorized Post", "content": "This should not be created"}
    response = client.post("/api/v1/posts", json=test_post)
    assert response.status_code == 401
    
    # Try to create a post with an invalid token test
    test_post = {"title": "Unauthorized Post", "content": "This should not be created"}
    invalid_token = "invalid.token.here"
    response = client.post(
        "/api/v1/posts",
        json=test_post,
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401

def test_missing_post():
    """Test handling of requests for non-existent posts"""
    # Create a mock user and valid token
    user_id = str(ObjectId())
    token = create_test_token(data={"id": user_id})
    
    # Generate a random ObjectId that doesn't exist
    non_existent_id = str(ObjectId())
    
    response = client.get(
        f"/api/v1/posts/{non_existent_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404  # Not Found

def test_upload_post_image(create_test_post):
    """Test uploading an image to a post"""
    post_id = create_test_post["post_id"]
    token = create_test_post["token"]
    
    # Create a test image file
    test_image = io.BytesIO(b"test image content")
    test_image.name = "test_image.jpg"
    
    response = client.post(
        f"/api/v1/posts/{post_id}/images",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test_image.jpg", test_image, "image/jpeg")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "filename" in data
    assert "url" in data
    
    # Clean up - remove created file
    if os.path.exists(data["url"].replace("http://localhost:8000/", "")):
        os.remove(data["url"].replace("http://localhost:8000/", ""))

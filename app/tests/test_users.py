from fastapi.testclient import TestClient
from app.main import app
import pytest
import os
from bson.objectid import ObjectId
from app.tests.test_utils import create_test_token, mock_user, mock_user_with_tokens
import io
from app.auth import verify_password, get_password_hash
from app.logger import setup_logging, get_logger

client = TestClient(app)

logger = get_logger(__name__)

logger.debug("Starting test_users.py")
logger.debug("Test API module loaded")
logger.debug("Test client created")

def test_read_main():
    response = client.get("/api/v1/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# === User Profile Update Tests ===
def test_get_current_user(mock_user):
    """Test getting the current user profile"""
    from app.database import db
    from datetime import datetime, timezone
    from jose import JWTError, jwt
    from app.auth import SECRET_KEY, ALGORITHM

    logger.info("*****Starting test_get_current_user")
    logger.debug("mock_user: %s", mock_user)

    # Create a token for authentication
    access_token = create_test_token({"id": mock_user}, token_type="access")
    logger.debug(f"Token: {access_token}")

    # Get token expiration from the payload
    payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    logger.debug(f"Decoded payload: {payload}")
    exp_timestamp = payload.get("exp")
    expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    logger.debug(f"Token expires at: {expires_at}")
    
    # Add the token as a TokenInfo object (matching the schema)
    db['users'].update_one(
        {"_id": ObjectId(mock_user)},
        {"$push": {"tokens": access_token}}
    )
    
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert data["id"] == mock_user

@pytest.fixture
def create_second_user():
    """Create a second user for duplicate email testing"""

    logger.debug("Starting create_second_user")

    # Create a test user ID in ObjectId format
    user_id = str(ObjectId())
    
    # Set up the database
    from app.database import db
    from app.auth import get_password_hash
    from datetime import datetime, timezone
    
    test_user = {
        "_id": ObjectId(user_id),
        "email": "second_user@example.com",
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

def test_update_email_already_taken(mock_user, create_second_user):
    """Test attempting to update to an email that's already taken by another user"""
    from app.database import db
    from datetime import datetime, timezone
    from jose import jwt
    from app.auth import SECRET_KEY, ALGORITHM
    
    logger.debug("*****Starting test_update_email_already_taken")

    # Create a token for authentication
    token = create_test_token(data={"id": mock_user})
    
    # Get token expiration from the payload
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    exp_timestamp = payload.get("exp")
    expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    
    # Add the token as TokenInfo object
    db['users'].update_one(
        {"_id": ObjectId(mock_user)},
        {"$push": {"tokens": token}}
    )
    
    # Get second user's email
    second_user = db['users'].find_one({"_id": ObjectId(create_second_user)})
    taken_email = second_user["email"]
    
    # Update request with already taken email
    response = client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": taken_email}
    )
    
    # Should fail with 400 Bad Request
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]
    
    # Verify database was not updated
    user_after = db['users'].find_one({"_id": ObjectId(mock_user)})
    assert user_after["email"] != taken_email

def test_update_user_unauthorized():
    """Test that unauthorized users cannot update profile"""
    # Try to update without a token
    response = client.put(
        "/api/v1/users/me",
        json={"email": "unauthorized@example.com"}
    )
    assert response.status_code == 401
    
    # Try with invalid token
    invalid_token = "invalid.token.here"
    response = client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {invalid_token}"},
        json={"email": "unauthorized@example.com"}
    )
    assert response.status_code == 401

# Test update_current_user function
def test_update_current_user(mock_user):
    """Test updating the current user's profile"""
    
    from app.database import db
    from datetime import datetime, timezone
    from jose import jwt
    from app.auth import SECRET_KEY, ALGORITHM

    logger.debug("*****Starting test_update_current_user")

    # Create a token for authentication
    token = create_test_token(data={"id": mock_user})
    # Get token expiration from the payload
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    exp_timestamp = payload.get("exp")
    expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    # Add the token as TokenInfo object
    db['users'].update_one(
        {"_id": ObjectId(mock_user)},
        {"$push": {"tokens": token}}
    )
    # Update request with new email
    response = client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "new_email@example.com"}
    )   
    assert response.status_code == 200
    # Verify database was updated
    user_after = db['users'].find_one({"_id": ObjectId(mock_user)})
    assert user_after["email"] == "new_email@example.com"
    # Verify token was added to the user's tokens
    tokens = user_after["tokens"]
    assert len(tokens) == 1
    assert tokens[0] == token
    # assert tokens[0]["expires_at"] == expires_at
    
    # Verify token was removed from other users
    other_users = db['users'].find({"_id": {"$ne": ObjectId(mock_user)}})
    for user in other_users:
        assert "tokens" not in user or token not in user["tokens"]

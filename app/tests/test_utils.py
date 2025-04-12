from datetime import datetime, timedelta, timezone
from jose import jwt
import pytest
from bson.objectid import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.database import db

def create_test_token(data: dict, expires_delta: timedelta = None, token_type: str = "access"):
    """
    Create a JWT token for testing purposes.
    
    Args:
        data: The payload data to include in the token
        expires_delta: Optional expiration time delta, defaults to 15 minutes
        token_type: Type of token - "access" or "refresh"
        
    Returns:
        A JWT token string
    """
    # Use the same SECRET_KEY as the application
    from app.auth import SECRET_KEY
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "token_type": token_type})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

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

@pytest.fixture
def mock_user_with_tokens():
    """Creates a mock user with both access and refresh tokens in the database"""
    # Create a test user ID in ObjectId format
    user_id = str(ObjectId())
    
    # Get auth utilities
    from app.database import db
    from app.auth import get_password_hash
    
    # Create test tokens
    access_token = create_test_token({"id": user_id}, token_type="access")
    refresh_token = create_test_token(
        {"id": user_id}, 
        expires_delta=timedelta(days=7),
        token_type="refresh"
    )
    
    # Create a test user with tokens
    test_user = {
        "_id": ObjectId(user_id),
        "email": "testuser_with_tokens@example.com",
        "hashed_password": get_password_hash("testpassword"),
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "tokens": [access_token, refresh_token]
    }
    
    # Insert the user in the database
    db['users'].insert_one(test_user)
    
    yield {"user_id": user_id, "access_token": access_token, "refresh_token": refresh_token}
    
    # Clean up - remove the test user
    db['users'].delete_one({"_id": ObjectId(user_id)})
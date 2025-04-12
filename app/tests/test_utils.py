from datetime import datetime, timedelta, timezone
from jose import jwt
import pytest
from bson.objectid import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.database import db

def create_test_token(data: dict, expires_delta: timedelta = None):
    """
    Create a JWT token for testing purposes.
    
    Args:
        data: The payload data to include in the token
        expires_delta: Optional expiration time delta, defaults to 15 minutes
        
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
    to_encode.update({"exp": expire})
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
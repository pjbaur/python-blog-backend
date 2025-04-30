import os
from datetime import datetime, timedelta, timezone
import jwt
import pytest
from bson.objectid import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.database import db
from app.logger import get_logger

logger = get_logger(__name__)

# Set testing environment variable for the s3_operations mock
os.environ["TESTING"] = "true"

def create_test_token(data: dict, expires_delta: timedelta = None, token_type: str = "access"):
    """
    This function creates tokens, and needs to be reconciled.
    Are these the cool tokens with expiry dates, or the old ones?

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

@pytest.fixture
def mock_user():
    """Create a test user and return the user ID"""
    from app.database import db
    
    user_id = str(ObjectId())
    db['users'].insert_one({
        "_id": ObjectId(user_id),
        "email": f"test.user.{user_id}@example.com",
        "hashed_password": "$2b$12$uKJUPbsJdWJoqm.n.Z1ME.26.dYnzKPyW4vZF8KWQUbW687MRbFpy",  # password is "password"
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.utcnow(),
        "tokens": []
    })
    
    yield user_id
    
    # Clean up
    db['users'].delete_one({"_id": ObjectId(user_id)})

@pytest.fixture
def mock_admin_user():
    """Create a mock admin user for testing admin endpoints"""
    # Create a test admin user ID
    user_id = str(ObjectId())
    
    # Set up the database user with admin privileges
    from app.database import db
    from app.auth import get_password_hash
    from datetime import datetime, timezone
    
    test_admin = {
        "_id": ObjectId(user_id),
        "email": "admin@example.com",
        "hashed_password": get_password_hash("adminpassword"),
        "is_active": True,
        "is_admin": True,  # Admin privileges
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "tokens": []
    }
    
    # Insert the admin user in the database
    db['users'].insert_one(test_admin)
    
    # Create a token for the admin user
    token = create_test_token(
        {"id": user_id}, token_type="access"
    )
    
    # Get token expiration from the payload
    from jose import jwt
    from app.auth import SECRET_KEY, ALGORITHM
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    exp_timestamp = payload.get("exp")
    expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    
    # Add the token as a TokenInfo object (matching the schema)
    db['users'].update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"tokens": token}}
    )
    
    yield {"user_id": user_id, "token": token}
    
    # Clean up - remove the test admin user
    db['users'].delete_one({"_id": ObjectId(user_id)})

@pytest.fixture
def mock_user_with_tokens():
    """Creates a mock user with both access and refresh tokens in the database
    
    I think this is creating old style tokens, not the new ones."""
    logger.debug("Creating mock user with tokens")  

    # Create a test user ID in ObjectId format
    user_id = str(ObjectId())
    logger.debug(f"User ID: {user_id}")
    
    # Get auth utilities
    from app.database import db
    from app.auth import get_password_hash
    from app.auth import SECRET_KEY, ALGORITHM
    
    # Create test tokens
    access_token = create_test_token({"id": user_id}, token_type="access")
    logger.debug(f"Access token: {access_token}")
    refresh_token = create_test_token(
        {"id": user_id}, 
        expires_delta=timedelta(days=7),
        token_type="refresh"
    )
    logger.debug(f"Refresh token: {refresh_token}")
    
    # Get token expirations from the payloads
    access_payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    access_exp = datetime.fromtimestamp(access_payload.get("exp"), tz=timezone.utc)
    
    refresh_payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    refresh_exp = datetime.fromtimestamp(refresh_payload.get("exp"), tz=timezone.utc)
    
    # Create a test user with tokens in TokenInfo format
    test_user = {
        "_id": ObjectId(user_id),
        "email": "testuser_with_tokens@example.com",
        "hashed_password": get_password_hash("testpassword"),
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "tokens": [ access_token, refresh_token ]
    }
    logger.debug(f"Test user: {test_user}")
    
    # Insert the user in the database
    db['users'].insert_one(test_user)
    
    yield {"user_id": user_id, "access_token": access_token, "refresh_token": refresh_token}
    
    # Clean up - remove the test user
    db['users'].delete_one({"_id": ObjectId(user_id)})
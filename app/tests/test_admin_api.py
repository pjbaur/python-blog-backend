from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime, timezone
import pytest
from bson.objectid import ObjectId
from app.tests.test_utils import create_test_token, mock_user, mock_user_with_tokens, mock_admin_user
from app.logger import setup_logging, get_logger

client = TestClient(app)

logger = get_logger(__name__)
setup_logging()

def test_admin_get_users(mock_admin_user):
    """Test that admin users can access the /admin/users endpoint"""
    logger.debug("*****Testing admin access to /admin/users endpoint")  
    
    token = mock_admin_user["token"]
    logger.debug(f"Using token: {token}")

    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Response content: {response.content}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Check that each user has the expected fields
    for user in data:
        assert "id" in user
        assert "email" in user
        assert "is_active" in user
        assert "is_admin" in user
        assert "tokens" in user

def test_non_admin_get_users(mock_user):
    """Test that non-admin users cannot access the /admin/users endpoint"""
    # Create a token for the non-admin user
    logger.debug("*****Testing non-admin access to /admin/users endpoint")

    token = create_test_token(data={"id": mock_user})
    logger.debug(f"Using token: {token}")

    # Add the token to the user's token list
    from app.database import db
    db['users'].update_one(
        {"_id": ObjectId(mock_user)},
        {"$push": {"tokens": token}}
    )
    
    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Should return a 403 Forbidden status
    assert response.status_code == 401

def test_unauthorized_admin_access():
    """Test that unauthorized requests cannot access admin endpoints"""
    # Try without a token
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 401
    
    # Try with an invalid token
    invalid_token = "invalid.token.here"
    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401
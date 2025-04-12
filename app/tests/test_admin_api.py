from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime, timezone
import pytest
from bson.objectid import ObjectId
from app.tests.test_utils import create_test_token, mock_user

client = TestClient(app)

@pytest.fixture
def mock_admin_user():
    """Create a mock admin user for testing admin endpoints"""
    # Create a test admin user ID
    user_id = str(ObjectId())
    
    # Set up the database user with admin privileges
    from app.database import db
    from app.auth import get_password_hash
    
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
        data={"id": user_id},
    )
    
    # Add the token to the user's token list
    db['users'].update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"tokens": token}}
    )
    
    yield {"user_id": user_id, "token": token}
    
    # Clean up - remove the test admin user
    db['users'].delete_one({"_id": ObjectId(user_id)})

def test_admin_get_users(mock_admin_user):
    """Test that admin users can access the /admin/users endpoint"""
    token = mock_admin_user["token"]
    
    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    
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
    token = create_test_token(data={"id": mock_user})
    
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
    assert response.status_code == 403

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
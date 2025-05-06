import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from bson.objectid import ObjectId

from app.main import app
from app.tests.test_utils import mock_user_with_tokens
from app.auth import verify_password, get_password_hash, verify_token
from app.database import db
from app.logger import get_logger

client = TestClient(app)
logger = get_logger(__name__)

class TestPasswordChange:
    """Test the password change functionality"""

    def test_strong_password_change_success(self, mock_user_with_tokens):
        """Test that password change works correctly when all inputs are valid"""
        access_token = mock_user_with_tokens["access_token"]
        user_id = mock_user_with_tokens["user_id"]
        
        # Get the current user to check current password
        user_before = db['users'].find_one({"_id": ObjectId(user_id)})
        current_password = "testpassword"  # From the mock_user_with_tokens fixture
        
        # Change password request
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": current_password,
                "new_password": "newPassword-OrangeOverhead123",
                "confirm_password": "newPassword-OrangeOverhead123"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Check that request was successful
        assert response.status_code == 200
        data = response.json()
        
        # Check response contains new tokens
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        
        # Get updated user and verify password was changed
        user_after = db['users'].find_one({"_id": ObjectId(user_id)})
        
        # Verify password was actually changed
        assert user_before["hashed_password"] != user_after["hashed_password"]
        assert verify_password("newPassword-OrangeOverhead123", user_after["hashed_password"])
        
        # Verify old tokens were invalidated
        assert access_token not in user_after["tokens"]
        
        # Verify new tokens are valid
        access_payload = verify_token(data["access_token"], token_type="access")
        refresh_payload = verify_token(data["refresh_token"], token_type="refresh")
        
        assert access_payload is not None
        assert refresh_payload is not None
        assert access_payload["id"] == user_id
        assert refresh_payload["id"] == user_id
        
        # Verify new tokens are stored in the database
        assert data["access_token"] in user_after["tokens"]
        assert data["refresh_token"] in user_after["tokens"]

    def test_incorrect_current_password(self, mock_user_with_tokens):
        """Test that password change fails when current password is incorrect"""
        access_token = mock_user_with_tokens["access_token"]
        
        # Change password request with incorrect current password
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "wrongpassword",
                "new_password": "newPassword-OrangeOverhead123",
                "confirm_password": "newPassword-OrangeOverhead123"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Check that request failed with correct error
        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["detail"]

    def test_mismatched_passwords(self, mock_user_with_tokens):
        """Test that password change fails when new password and confirmation don't match"""
        access_token = mock_user_with_tokens["access_token"]
        
        # Change password request with mismatched new passwords
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "testpassword",
                "new_password": "newPassword-OrangeOverhead123",
                "confirm_password": "differentpassword"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Check that request failed with correct error
        assert response.status_code == 400
        assert "New password and confirmation don't match" in response.json()["detail"]

    def test_unauthorized_password_change(self):
        """Test that password change fails when not authenticated"""
        # Change password request without auth token
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "testpassword",
                "new_password": "newPassword-OrangeOverhead123",
                "confirm_password": "newPassword-OrangeOverhead123"
            }
        )
        
        # Check that request failed with 401 Unauthorized
        assert response.status_code == 401

    def test_old_token_invalidated(self, mock_user_with_tokens):
        """Test that old tokens are invalidated after password change"""
        access_token = mock_user_with_tokens["access_token"]
        user_id = mock_user_with_tokens["user_id"]
        
        # Change password successfully
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "testpassword",
                "new_password": "newPassword-OrangeOverhead123",
                "confirm_password": "newPassword-OrangeOverhead123"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Try to use the old token for an authenticated request
        me_response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Check that the old token is now invalid
        assert me_response.status_code == 401

    def test_password_reuse_prevention(self, mock_user_with_tokens):
        """Test that password change fails when trying to reuse a previous password"""
        access_token = mock_user_with_tokens["access_token"]
        user_id = mock_user_with_tokens["user_id"]
        initial_password = "testpassword"  # From the mock_user_with_tokens fixture
        
        # First password change - change to a new password
        first_change_response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": initial_password,
                "new_password": "newPassword-OrangeOverhead123",
                "confirm_password": "newPassword-OrangeOverhead123"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Get the new access token for subsequent requests
        new_access_token = first_change_response.json()["access_token"]
        
        # Try to change back to the original password - should be rejected
        reuse_response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "newPassword-OrangeOverhead123",
                "new_password": initial_password,
                "confirm_password": initial_password
            },
            headers={"Authorization": f"Bearer {new_access_token}"}
        )
        
        # Check that the request failed with the correct error
        assert reuse_response.status_code == 400
        assert "Password cannot be reused" in reuse_response.json()["detail"]
        
        # Verify the password remains the new one
        user_after = db['users'].find_one({"_id": ObjectId(user_id)})
        assert verify_password("newPassword-OrangeOverhead123", user_after["hashed_password"])
        
        # Verify that the password history has been updated
        assert len(user_after.get("password_history", [])) > 0
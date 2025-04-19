import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.main import app
from app.tests.test_utils import mock_user, mock_user_with_tokens, create_test_token
from app.auth import SECRET_KEY, verify_token
from app.database import db
from app.logger import setup_logging, get_logger
from bson.objectid import ObjectId

client = TestClient(app)

logger = get_logger(__name__)

class TestRefreshToken:
    """Test the refresh token functionality"""

    def test_login_returns_refresh_token(self):
        """Test that login returns both access and refresh tokens"""

        logger.debug("Testing login_returns_refresh_token()")

        # Create a test user to login with
        from app.auth import get_password_hash
        
        email = "refresh_test_user@example.com"
        password = "testpassword123"
        
        # Create the user in the database
        user_data = {
            "email": email,
            "hashed_password": get_password_hash(password),
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.now(timezone.utc),
            "tokens": []
        }
        
        result = db['users'].insert_one(user_data)
        user_id = result.inserted_id
        logger.debug(f"Inserted user with ID: {user_id}")
        logger.debug(f"User data: {user_data}")

        try:
            # Login with the user
            response = client.post(
                "/api/v1/auth/login",
                json={"email": email, "password": password}
            )
            
            # Check that the login was successful and returned both tokens
            assert response.status_code == 200
            data = response.json()

            logger.debug(f"Login response data: {data}")

            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"
            
            # Verify the tokens are valid
            access_payload = verify_token(data["access_token"], token_type="access")
            refresh_payload = verify_token(data["refresh_token"], token_type="refresh")
            logger.debug(f"Access payload: {access_payload}")
            logger.debug(f"Refresh payload: {refresh_payload}")
            
            assert access_payload is not None
            assert refresh_payload is not None
            assert access_payload["id"] == str(user_id)
            assert refresh_payload["id"] == str(user_id)
            
            # Verify tokens are stored in the database
            user = db['users'].find_one({"_id": user_id})
            logger.debug(f"user: {user}")
            logger.debug(f"User tokens: {user['tokens']}")
            
            # Check for tokens in TokenInfo format
            token_values = user["tokens"]
            assert data["access_token"] in token_values
            assert data["refresh_token"] in token_values
            
        finally:
            # Clean up
            db['users'].delete_one({"_id": user_id})

    def test_refresh_token_endpoint(self, mock_user_with_tokens):
        """Test that the refresh token endpoint returns a new access token"""
        logger.debug(f"Testing refresh_token_endpoint()")

        refresh_token = mock_user_with_tokens["refresh_token"]
        logger.debug(f"Refresh token: {refresh_token}")

        user_id = mock_user_with_tokens["user_id"]
        logger.debug(f"User ID: {user_id}")
        
        # At this point, the user object has the old style tokens in it.

        # Dump the database document for user_id
        user = db['users'].find_one({"_id": ObjectId(user_id)})
        logger.debug(f"A-User: {user}")

        # Call the refresh endpoint
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        logger.debug(f"Response: {response}")
        
        # Dump the database document for user_id
        user = db['users'].find_one({"_id": ObjectId(user_id)})
        logger.debug(f"B-User: {user}")

        # Check that the request was successful and returned a new access token
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Verify the new access token is valid
        new_access_payload = verify_token(data["access_token"], token_type="access")
        # Dump the database document for user_id
        user = db['users'].find_one({"_id": ObjectId(user_id)})
        logger.debug(f"C-User: {user}")
        assert new_access_payload is not None
        assert new_access_payload["id"] == user_id
        
        # Verify the new access token is stored in the database
        user = db['users'].find_one({"_id": ObjectId(user_id)})
        logger.debug(f"D-User: {user}")
        # Check for token in str format
        token_values = user["tokens"]
        assert data["access_token"] in token_values

    def test_refresh_with_invalid_token(self):
        """Test that refresh fails with an invalid refresh token"""
        # Create an invalid token
        invalid_token = "invalid.refresh.token"
        
        # Call the refresh endpoint with the invalid token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": invalid_token}
        )
        
        # Check that the request failed
        assert response.status_code == 401
        assert "Invalid or expired refresh token" in response.json()["detail"]

    def test_refresh_with_expired_token(self, mock_user):
        """Test that refresh fails with an expired refresh token"""
        # Create an expired refresh token
        expired_token = create_test_token(
            {"id": mock_user},
            expires_delta=timedelta(seconds=-1),  # Expired
            token_type="refresh"
        )
        
        # Add the token to the user's token list
        db['users'].update_one(
            {"_id": ObjectId(mock_user)},
            {"$push": {"tokens": expired_token}}
        )
        
        # Call the refresh endpoint
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": expired_token}
        )
        
        # Check that the request failed
        assert response.status_code == 401
        assert "Invalid or expired refresh token" in response.json()["detail"]

    def test_refresh_with_access_token(self, mock_user_with_tokens):
        """Test that refresh fails when using an access token instead of a refresh token"""
        access_token = mock_user_with_tokens["access_token"]
        
        # Call the refresh endpoint with an access token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token}
        )
        
        # Check that the request failed
        assert response.status_code == 401
        assert "Invalid or expired refresh token" in response.json()["detail"]

    def test_refresh_with_nonexistent_user(self):
        """Test that refresh fails when the user doesn't exist"""
        # Create a token for a non-existent user
        non_existent_id = str(ObjectId())
        refresh_token = create_test_token(
            {"id": non_existent_id},
            token_type="refresh"
        )
        
        # Call the refresh endpoint
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        # Check that the request failed
        assert response.status_code == 401
        assert "Invalid or expired refresh token" in response.json()["detail"]

class TestLogout:
    """Test the logout functionality"""

    def test_logout_endpoint(self, mock_user_with_tokens):
        """Test that the logout endpoint invalidates the refresh token"""
        refresh_token = mock_user_with_tokens["refresh_token"]
        user_id = mock_user_with_tokens["user_id"]
        
        # Call the logout endpoint
        response = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token}
        )
        
        # Check that the request was successful (204 No Content)
        assert response.status_code == 204
        assert response.content == b''
        
        # Verify the token was removed from the database
        user = db['users'].find_one({"_id": ObjectId(user_id)})
        token_values = user["tokens"]
        assert refresh_token not in token_values

    def test_logout_with_invalid_token(self):
        """Test that logout fails with an invalid token"""
        # Create an invalid token
        invalid_token = "invalid.refresh.token"
        
        # Call the logout endpoint with the invalid token
        response = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": invalid_token}
        )
        
        # Check that the request failed
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    def test_logout_removes_only_specific_token(self, mock_user_with_tokens):
        """Test that logout only removes the specific token, not all tokens"""
        refresh_token = mock_user_with_tokens["refresh_token"]
        access_token = mock_user_with_tokens["access_token"]
        user_id = mock_user_with_tokens["user_id"]
        
        # Call the logout endpoint
        response = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token}
        )
        
        # Check that the request was successful
        assert response.status_code == 204
        
        # Verify only the refresh token was removed
        user = db['users'].find_one({"_id": ObjectId(user_id)})
        
        # Extract token values from TokenInfo objects
        token_values = user["tokens"]
        
        # Check refresh token was removed but access token still exists
        assert refresh_token not in token_values
        assert access_token in token_values

    def test_logout_with_both_tokens(self, mock_user_with_tokens):
        """Test that logout can invalidate both access and refresh tokens when provided"""
        refresh_token = mock_user_with_tokens["refresh_token"]
        access_token = mock_user_with_tokens["access_token"]
        user_id = mock_user_with_tokens["user_id"]
        
        # Call the logout endpoint with both tokens
        response = client.post(
            "/api/v1/auth/logout",
            json={
                "refresh_token": refresh_token,
                "access_token": access_token
            }
        )
        
        # Check that the request was successful
        assert response.status_code == 204
        
        # Verify both tokens were removed from the database
        user = db['users'].find_one({"_id": ObjectId(user_id)})
        
        # Extract token values from TokenInfo objects
        token_values = [token_info["token"] for token_info in user["tokens"]]
        
        assert refresh_token not in token_values
        assert access_token not in token_values
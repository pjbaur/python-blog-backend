from fastapi import APIRouter, HTTPException, Depends, status
from .. import auth, crud, schemas
from ..models import UserModel
from datetime import timedelta, datetime, timezone
from ..logger import get_logger
from ..password_validation import PasswordPolicy

logger = get_logger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

# User Registration
@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreateRequest):
    logger.info(f"Registration attempt for email: {user.email}")
    existing_user = crud.get_user_by_email(user.email)
    if existing_user:
        logger.warning(f"Registration failed: Email already registered: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate password using PasswordPolicy
    password_policy = PasswordPolicy()
    is_valid, password_errors = password_policy.validate_password(user.password)
    if not is_valid:
        logger.warning(f"Registration failed: Password validation errors for {user.email}: {password_errors}")
        raise HTTPException(
            status_code=422, 
            detail="Password validation failed",
            errors=password_errors)

    hashed_password = auth.get_password_hash(user.password)
    user_model = UserModel(
        email=user.email,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        password_history=[]  # Initialize empty password history
    )
    new_user = crud.create_user(user_model)
    logger.info(f"User registered successfully: {user.email}")
    return new_user

# User Login
@router.post("/login", response_model=schemas.TokenResponse)
def login_user(login_data: schemas.LoginRequest):
    """ Login endpoint for user authentication.

    This endpoint uses tokens and needs to be reconciled.

    I think the story starts here, because this creates the token and stores it in the database.
    """
    logger.info(f"Login attempt for email: {login_data.email}")
    user = auth.authenticate_user(login_data.email, login_data.password)
    if not user:
        logger.warning(f"Login failed: Incorrect credentials for {login_data.email}")
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # Create both access and refresh tokens
    access_token, refresh_token = auth.create_token_pair(
        data={"id": str(user.id)}
    )
    
    logger.debug(f">>>>>Access token created: {access_token}")
    logger.debug(f">>>>>Refresh token created: {refresh_token}")

    logger.info(f"Login successful for user: {login_data.email}")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

# Implement refresh token endpoint
@router.post("/refresh", response_model=schemas.TokenResponse)
def refresh_token(refresh_data: schemas.RefreshTokenRequest):
    """ Refresh token endpoint.

    This endpoint uses tokens and needs to be reconciled.
    """
    logger.info("Token refresh requested")
    
    # Verify the refresh token
    payload = auth.verify_token(refresh_data.refresh_token, token_type="refresh")
    if not payload:
        logger.warning("Refresh token validation failed")
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    user_id = payload.get("id")
    
    # Check if user exists
    user = crud.get_user_by_id(user_id)
    if not user:
        logger.warning(f"User not found for refresh token, ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate new access token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = auth.create_access_token(
        data={"id": user_id},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Token refreshed successfully for user ID: {user_id}")
    return {"access_token": new_access_token, "token_type": "bearer"}

# Implement verify token endpoint
@router.post("/verify-token")
def verify_token(verify_data: schemas.TokenVerifyRequest):
    """ Verify token endpoint.
    
    This endpoint verifies if the provided token is still valid.
    It returns information about the token's validity, user ID, token type, and expiration.
    """
    logger.info("Token verification requested")
    
    # Extract token from request
    token = verify_data.token
    logger.debug(f"Token to verify: {token}")
    if not token:
        logger.warning("No token provided for verification")
        # Return invalid token response instead of raising an error
        return schemas.InvalidTokenResponse()
        
    # Check if the token is a valid JWT
    if not auth.is_jwt_token(token):
        logger.warning("Invalid token format")
        raise HTTPException(status_code=400, detail="Invalid token format")
    # Check if the token is expired
    if auth.is_token_expired(token):
        logger.warning("Token is expired")
        return schemas.InvalidTokenResponse()
    
    # Verify the token without specifying a type to allow either access or refresh tokens
    payload = auth.verify_token(token)
    logger.debug(f"Token payload: {payload}")

    if not payload:
        logger.warning("Token validation failed")
        return schemas.InvalidTokenResponse()
    
    # Extract token information
    user_id = payload.get("id")
    token_type = payload.get("token_type")
    expires_at = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
    
    logger.info(f"Token verified successfully for user ID: {user_id}")
    return schemas.TokenVerifyResponse(
        is_valid=True,
        user_id=user_id,
        token_type=token_type,
        expires_at=expires_at
    )

# Implement logout endpoint
@router.post("/logout", status_code=204)
def logout_user(logout_data: schemas.LogoutRequest):
    """ Logout endpoint.
    This endpoint uses tokens and needs to be reconciled.
    """
    logger.info("routers/auth.py::logout_user() -- Logout requested")
    
    # Verify the refresh token
    payload = auth.verify_token(logout_data.refresh_token)
    if not payload:
        logger.warning("Invalid refresh token during logout")
        raise HTTPException(status_code=401, detail="Invalid token")
    
    logger.debug("payload: ", payload)

    # Prepare tokens to invalidate
    tokens_to_invalidate = [logout_data.refresh_token]
    
    # Add access token if provided
    if logout_data.access_token:
        # Verify the access token belongs to the same user
        access_payload = auth.verify_token(logout_data.access_token, token_type="access")
        if access_payload and access_payload.get("id") == payload.get("id"):
            tokens_to_invalidate.append(logout_data.access_token)
        else:
            logger.warning("Invalid access token during logout")
    
    # Invalidate all provided tokens
    success = auth.invalidate_tokens(tokens_to_invalidate)
    
    if not success:
        logger.warning("Failed to invalidate tokens during logout")
        raise HTTPException(status_code=500, detail="Failed to logout")
    
    logger.info(f"User logged out successfully, ID: {payload.get('id')}")
    return None

# Change password endpoint
@router.post("/change-password", response_model=schemas.TokenResponse)
async def change_password(
    password_data: schemas.PasswordChangeRequest,
    current_user: UserModel = Depends(auth.get_current_user)
):
    """Change the password for the current user.
    This endpoint verifies the current password, checks for password reuse,
    validates the new password, and updates the password in the database.
    """
    logger.info(f"Password change requested for user: {current_user}")
    logger.debug(f"Password change data: {password_data}")
    
    # Verify current password
    if not auth.verify_password(password_data.current_password, current_user.hashed_password):
        logger.warning(f"Password change failed: Current password incorrect for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Verify new password and confirmation match
    if password_data.new_password != password_data.confirm_password:
        logger.warning(f"Password change failed: New password and confirmation don't match for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation don't match"
        )
    
    password_policy = PasswordPolicy()
    
    # Check if password is being reused
    is_reused, reuse_error = password_policy.check_password_reuse(
        password_data.new_password, 
        current_user.password_history
    )
    
    if is_reused:
        logger.warning(f"Password change failed: Password reuse detected for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=reuse_error
        )
    
    # Validate password strength
    is_valid, password_errors = password_policy.validate_password(password_data.new_password)
    if not is_valid:
        logger.warning(f"Password change failed: New password validation errors for {current_user.email}: {password_errors}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New password validation failed",
            errors=password_errors
        )

    # Hash new password
    hashed_password = auth.get_password_hash(password_data.new_password)
    
    # Get the maximum history size from the policy
    max_history_size = password_policy.config["password_history_count"]
    
    # Prepare password history update
    password_history = current_user.password_history.copy() if current_user.password_history else []
    
    # Add current password to history
    if current_user.hashed_password not in password_history:
        password_history.append(current_user.hashed_password)
    
    # Trim history if it exceeds the maximum size
    if len(password_history) > max_history_size:
        password_history = password_history[-max_history_size:]
    
    # Update user with new password and history
    updates = {
        "hashed_password": hashed_password,
        "password_history": password_history,
        "updated_at": datetime.now(timezone.utc)
    }
    
    result = crud.update_user(str(current_user.id), updates)
    if result.modified_count == 0:
        logger.warning(f"Password change failed: Database update failed for user: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )

    # Store current tokens for invalidation
    current_tokens = current_user.tokens.copy() if current_user.tokens else []
    
    # Invalidate all existing tokens
    if current_tokens:
        auth.invalidate_tokens(current_tokens)
        logger.debug(f"All tokens invalidated for user: {current_user.email}")
    
    # Create new tokens
    token_data = {"id": str(current_user.id), "email": current_user.email}
    access_token, refresh_token = auth.create_token_pair(token_data)
    
    logger.info(f"Password changed successfully for user: {current_user.email}")
    
    # Return new tokens
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

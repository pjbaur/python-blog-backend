from fastapi import APIRouter, HTTPException, Depends
from .. import auth, crud, schemas
from ..models import UserModel
from datetime import timedelta, datetime, timezone
from ..logger import get_logger

# Set up logger
logger = get_logger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

# User Registration
@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate):
    logger.info(f"Registration attempt for email: {user.email}")
    existing_user = crud.get_user_by_email(user.email)
    if existing_user:
        logger.warning(f"Registration failed: Email already registered: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    user_model = UserModel(
        email=user.email,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    new_user = crud.create_user(user_model)
    logger.info(f"User registered successfully: {user.email}")
    return new_user

# User Login
@router.post("/login", response_model=schemas.Token)
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
@router.post("/refresh", response_model=schemas.Token)
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

# Implement logout endpoint
@router.post("/logout", status_code=204)
def logout_user(logout_data: schemas.LogoutRequest):
    """ Logout endpoint.
    This endpoint uses tokens and needs to be reconciled.
    """
    logger.info("Logout requested")
    
    # Verify the refresh token
    payload = auth.verify_token(logout_data.refresh_token)
    if not payload:
        logger.warning("Invalid refresh token during logout")
        raise HTTPException(status_code=401, detail="Invalid token")
    
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
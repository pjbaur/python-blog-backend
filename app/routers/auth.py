from fastapi import APIRouter, HTTPException
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
    logger.info(f"Login attempt for email: {login_data.email}")
    user = auth.authenticate_user(login_data.email, login_data.password)
    if not user:
        logger.warning(f"Login failed: Incorrect credentials for {login_data.email}")
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"id": str(user.id)}, expires_delta=access_token_expires
    )
    logger.info(f"Login successful for user: {login_data.email}")
    return {"access_token": access_token, "token_type": "bearer"}

# TODO: Implement refresh token endpoint as specified in API doc
@router.post("/refresh", response_model=schemas.Token)
def refresh_token(refresh_data: schemas.RefreshTokenRequest):
    # This is a placeholder - you'll need to implement token refresh logic
    logger.info("Token refresh requested")
    raise HTTPException(status_code=501, detail="Token refresh not yet implemented")

# TODO: Implement logout endpoint as specified in API doc
@router.post("/logout")
def logout_user(logout_data: schemas.LogoutRequest, current_user: UserModel = auth.get_current_user):
    # This is a placeholder - you'll need to implement logout logic
    logger.info(f"Logout requested for user: {current_user.email}")
    raise HTTPException(status_code=501, detail="Logout not yet implemented")
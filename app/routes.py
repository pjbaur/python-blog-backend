from fastapi import APIRouter, Depends, HTTPException, Query
from . import auth, crud, schemas
from .models import UserModel
from datetime import timedelta, datetime, timezone
from .logger import get_logger
from typing import List
from .routers import posts

# Set up logger
logger = get_logger(__name__)

router = APIRouter()

# Include routers from modules
router.include_router(posts.router)

# User Registration
@router.post("/users/register", response_model=schemas.UserResponse)
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
@router.post("/auth/login", response_model=schemas.Token)
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

# Get Current User
@router.get("/users/me", response_model=schemas.UserResponse)
async def get_current_user(current_user: UserModel = Depends(auth.get_current_user)):
    logger.debug(f"Current user info requested: {current_user.email}")
    return current_user

# Admin: Get All Users
@router.get("/admin/users", response_model=list[schemas.UserResponse])
async def admin_get_users(current_user: UserModel = Depends(auth.get_current_user)):
    logger.info(f"Admin request to get all users from: {current_user.email}")
    if not current_user.is_admin:
        logger.warning(f"Unauthorized admin access attempt by: {current_user.email}")
        raise HTTPException(status_code=403, detail="Not authorized")
    users = crud.get_all_users()
    
    # Process each user to add token expiration info
    for user in users:
        if user.tokens:
            token_info_list = []
            for token in user.tokens:
                try:
                    # Decode the token to get expiration time
                    payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
                    exp_timestamp = payload.get("exp")
                    if exp_timestamp:
                        # Convert unix timestamp to datetime
                        expires_at = datetime.fromtimestamp(exp_timestamp)
                        token_info_list.append(schemas.TokenInfo(token=token, expires_at=expires_at))
                except auth.JWTError:
                    # Skip invalid tokens
                    logger.debug(f"Invalid token found for user: {user.email}")
                    continue
            user.tokens = token_info_list
        else:
            user.tokens = []
    
    logger.info(f"Returning data for {len(users)} users")    
    return users

# Healthcheck endpoint
@router.get("/healthcheck")
def healthcheck():
    logger.debug("Healthcheck endpoint called")
    return {"status": "ok"}
from fastapi import APIRouter, Depends, HTTPException, Query
from . import auth, crud, schemas
from .models import UserModel
from datetime import timedelta, datetime, timezone
from .logger import get_logger
from typing import List
from .routers import posts

# Set up logger
logger = get_logger(__name__)

# Create main API router with /api/v1 prefix
router = APIRouter(prefix="/api/v1")

# Authentication router
auth_router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

# User router
user_router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Admin router - keeping admin routes separate for clear access control
admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

# User Registration
@auth_router.post("/register", response_model=schemas.UserResponse)
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
@auth_router.post("/login", response_model=schemas.Token)
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
@auth_router.post("/refresh", response_model=schemas.Token)
def refresh_token(refresh_data: schemas.RefreshTokenRequest):
    # This is a placeholder - you'll need to implement token refresh logic
    logger.info("Token refresh requested")
    raise HTTPException(status_code=501, detail="Token refresh not yet implemented")

# TODO: Implement logout endpoint as specified in API doc
@auth_router.post("/logout")
def logout_user(logout_data: schemas.LogoutRequest, current_user: UserModel = Depends(auth.get_current_user)):
    # This is a placeholder - you'll need to implement logout logic
    logger.info(f"Logout requested for user: {current_user.email}")
    raise HTTPException(status_code=501, detail="Logout not yet implemented")

# Get Current User
@user_router.get("/me", response_model=schemas.UserResponse)
async def get_current_user(current_user: UserModel = Depends(auth.get_current_user)):
    logger.debug(f"Current user info requested: {current_user.email}")
    return current_user

# TODO: Implement get user by ID endpoint as specified in API doc
@user_router.get("/{user_id}", response_model=schemas.UserPublicResponse)
async def get_user_by_id(user_id: str):
    logger.info(f"User info requested for ID: {user_id}")
    user = crud.get_user_by_id(user_id)
    if not user:
        logger.warning(f"User not found with ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    return user

# TODO: Implement update user endpoint as specified in API doc
@user_router.put("/me", response_model=schemas.UserResponse)
async def update_current_user(
    user_data: schemas.UserUpdate,
    current_user: UserModel = Depends(auth.get_current_user)
):
    logger.info(f"Update requested for user: {current_user.email}")
    # This is a placeholder - you'll need to implement user update logic
    raise HTTPException(status_code=501, detail="User update not yet implemented")

# Implementation of user posts endpoint as specified in API document
@user_router.get("/{user_id}/posts", response_model=List[schemas.PostResponse])
async def get_user_posts(
    user_id: str,
    page: int = Query(0, description="Page number (pagination)"),
    limit: int = Query(10, description="Maximum number of posts to return"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    order: str = Query("desc", description="Sort order (asc or desc)")
):
    logger.info(f"Retrieving posts for user: {user_id} with page={page}, limit={limit}")
    posts = crud.get_posts_by_author(user_id, limit=limit, skip=page*limit)
    return posts

# Admin: Get All Users
@admin_router.get("/users", response_model=list[schemas.UserResponse])
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

# Healthcheck endpoint - keeping outside the API versioning since it's a system endpoint
@router.get("/healthcheck")
def healthcheck():
    logger.debug("Healthcheck endpoint called")
    return {"status": "ok"}

# Include all the routers
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(admin_router)

# Include routers from modules - updating to match API design
router.include_router(posts.router)
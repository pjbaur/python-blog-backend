from fastapi import APIRouter, Depends, HTTPException, Query
from . import auth, crud, schemas
from .models import UserModel, PostModel
from datetime import timedelta, datetime, timezone
import os
from .logger import get_logger
from typing import List, Optional

# Make sure we have access to JWTError
from .auth import JWTError

# Set up logger
logger = get_logger(__name__)

router = APIRouter()

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

# Post endpoints
@router.post("/posts", response_model=schemas.PostResponse)
async def create_post(
    post_data: schemas.PostCreate,
    current_user: UserModel = Depends(auth.get_current_user)
):
    logger.info(f"Creating new post for user: {current_user.email}")
    # Create a new post model
    post = PostModel(
        title=post_data.title,
        content=post_data.content,
        author_id=str(current_user.id),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    # Save to database
    created_post = crud.create_post(post)
    logger.info(f"Post created with ID: {created_post.id}")
    return created_post

@router.get("/posts", response_model=List[schemas.PostResponse])
async def get_all_posts(
    skip: int = Query(0, description="Number of posts to skip"),
    limit: int = Query(10, description="Maximum number of posts to return")
):
    logger.info(f"Retrieving posts with skip={skip}, limit={limit}")
    posts = crud.get_all_posts(limit=limit, skip=skip)
    return posts

@router.get("/posts/{post_id}", response_model=schemas.PostResponse)
async def get_post_by_id(post_id: str):
    logger.info(f"Retrieving post by ID: {post_id}")
    post = crud.get_post_by_id(post_id)
    if not post:
        logger.warning(f"Post not found with ID: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.get("/users/{author_id}/posts", response_model=List[schemas.PostResponse])
async def get_posts_by_author(
    author_id: str,
    skip: int = Query(0, description="Number of posts to skip"),
    limit: int = Query(10, description="Maximum number of posts to return")
):
    logger.info(f"Retrieving posts by author: {author_id}")
    posts = crud.get_posts_by_author(author_id, limit=limit, skip=skip)
    return posts

@router.put("/posts/{post_id}", response_model=schemas.PostResponse)
async def update_post(
    post_id: str,
    post_data: schemas.PostCreate,
    current_user: UserModel = Depends(auth.get_current_user)
):
    logger.info(f"Updating post with ID: {post_id}")
    # Check if post exists
    existing_post = crud.get_post_by_id(post_id)
    if not existing_post:
        logger.warning(f"Post not found with ID: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")
        
    # Check if user is the author
    if existing_post.author_id != str(current_user.id) and not current_user.is_admin:
        logger.warning(f"Unauthorized update attempt by user: {current_user.email}")
        raise HTTPException(status_code=403, detail="You can only update your own posts")
        
    # Update post
    updates = {
        "title": post_data.title,
        "content": post_data.content,
        "updated_at": datetime.now(timezone.utc)
    }
    crud.update_post(post_id, updates)
    
    # Get updated post
    updated_post = crud.get_post_by_id(post_id)
    logger.info(f"Post updated: {post_id}")
    return updated_post

@router.delete("/posts/{post_id}", status_code=204)
async def delete_post(
    post_id: str,
    current_user: UserModel = Depends(auth.get_current_user)
):
    logger.info(f"Deleting post with ID: {post_id}")
    # Check if post exists
    existing_post = crud.get_post_by_id(post_id)
    if not existing_post:
        logger.warning(f"Post not found with ID: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")
        
    # Check if user is the author or admin
    if existing_post.author_id != str(current_user.id) and not current_user.is_admin:
        logger.warning(f"Unauthorized delete attempt by user: {current_user.email}")
        raise HTTPException(status_code=403, detail="You can only delete your own posts")
    
    # Delete post
    crud.delete_post(post_id)
    logger.info(f"Post deleted: {post_id}")
    return None

@router.get("/posts/search/", response_model=List[schemas.PostResponse])
async def search_posts(
    query: str,
    skip: int = Query(0, description="Number of posts to skip"),
    limit: int = Query(10, description="Maximum number of posts to return")
):
    logger.info(f"Searching posts with query: {query}")
    posts = crud.search_posts(query, limit=limit, skip=skip)
    return posts
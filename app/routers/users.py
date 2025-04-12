from fastapi import APIRouter, Depends, HTTPException, Query
from .. import auth, crud, schemas
from ..models import UserModel
from ..logger import get_logger
from typing import List

# Set up logger
logger = get_logger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Get Current User
@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user(current_user: UserModel = Depends(auth.get_current_user)):
    logger.debug(f"Current user info requested: {current_user.email}")
    return current_user

# Get user by ID endpoint
@router.get("/{user_id}", response_model=schemas.UserPublicResponse)
async def get_user_by_id(user_id: str):
    logger.info(f"User info requested for ID: {user_id}")
    user = crud.get_user_by_id(user_id)
    if not user:
        logger.warning(f"User not found with ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    return user

# TODO: Implement update user endpoint as specified in API doc
@router.put("/me", response_model=schemas.UserResponse)
async def update_current_user(
    user_data: schemas.UserUpdate,
    current_user: UserModel = Depends(auth.get_current_user)
):
    logger.info(f"Update requested for user: {current_user.email}")
    # This is a placeholder - you'll need to implement user update logic
    raise HTTPException(status_code=501, detail="User update not yet implemented")

# Implementation of user posts endpoint as specified in API document
@router.get("/{user_id}/posts", response_model=List[schemas.PostResponse])
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
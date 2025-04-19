from fastapi import APIRouter, Depends, HTTPException, Query, status
from .. import auth, crud, schemas
from ..models import UserModel
from ..logger import get_logger
from typing import List
from datetime import datetime, timezone

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

# Update user profile endpoint
@router.put("/me", response_model=schemas.UserResponse)
async def update_current_user(
    user_data: schemas.UserUpdate,
    current_user: UserModel = Depends(auth.get_current_user)
):
    logger.info(f"Update requested for user: {current_user.email}")
    
    # Prepare updates dictionary
    updates = {"updated_at": datetime.now(timezone.utc)}
    
    # Update email if provided
    if user_data.email is not None and user_data.email != current_user.email:
        # Check if email is already taken
        existing_user = crud.get_user_by_email(user_data.email)
        if existing_user and str(existing_user.id) != str(current_user.id):
            logger.warning(f"Email already taken: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        updates["email"] = user_data.email
    
    # Update password if provided
    if user_data.password is not None:
        hashed_password = auth.get_password_hash(user_data.password)
        updates["hashed_password"] = hashed_password
    
    # Only update if there are changes
    if len(updates) > 1:  # More than just updated_at
        result = crud.update_user(str(current_user.id), updates)
        if result.modified_count == 0:
            logger.warning(f"No changes made to user: {current_user.id}")
    
    # Get and return the updated user
    updated_user = crud.get_user_by_id(str(current_user.id))
    logger.info(f"User updated successfully: {updated_user.email}")
    return updated_user

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
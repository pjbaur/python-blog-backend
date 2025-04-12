from fastapi import APIRouter, Depends, HTTPException, Query
from .. import auth, crud, schemas
from ..models import UserModel, PostModel
from datetime import datetime, timezone
from ..logger import get_logger
from typing import List

# Set up logger
logger = get_logger(__name__)

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)

@router.post("", response_model=schemas.PostResponse)
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

@router.get("", response_model=List[schemas.PostResponse])
async def get_all_posts(
    skip: int = Query(0, description="Number of posts to skip", alias="page"),
    limit: int = Query(10, description="Maximum number of posts to return"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    order: str = Query("desc", description="Sort order (asc or desc)"),
    category: str = Query(None, description="Filter by category"),
    hashtag: str = Query(None, description="Filter by hashtag")
):
    logger.info(f"Retrieving posts with skip={skip}, limit={limit}")
    posts = crud.get_all_posts(limit=limit, skip=skip)
    # Note: category and hashtag filtering not yet implemented
    return posts

@router.get("/{post_id}", response_model=schemas.PostResponse)
async def get_post_by_id(post_id: str):
    logger.info(f"Retrieving post by ID: {post_id}")
    post = crud.get_post_by_id(post_id)
    if not post:
        logger.warning(f"Post not found with ID: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.put("/{post_id}", response_model=schemas.PostResponse)
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

@router.delete("/{post_id}")
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
    return {"detail": "Post successfully deleted"}

# Move this to the users router as specified in the API doc
# This endpoint should be at /api/v1/users/{user_id}/posts
@router.get("/user/{author_id}", response_model=List[schemas.PostResponse], deprecated=True)
async def get_posts_by_author(
    author_id: str,
    skip: int = Query(0, description="Number of posts to skip"),
    limit: int = Query(10, description="Maximum number of posts to return")
):
    logger.info(f"Retrieving posts by author: {author_id}")
    logger.warning("This endpoint is deprecated. Use /api/v1/users/{user_id}/posts instead")
    posts = crud.get_posts_by_author(author_id, limit=limit, skip=skip)
    return posts
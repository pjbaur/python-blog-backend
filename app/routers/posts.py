from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from .. import auth, crud, schemas
from ..models import UserModel, PostModel
from datetime import datetime, timezone
from ..logger import get_logger
from typing import List, Optional
import os
import uuid
from bson.objectid import ObjectId

logger = get_logger(__name__)

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)

@router.post("", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
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
        categories=post_data.categories if post_data.categories else [],
        is_published=post_data.is_published if post_data.is_published is not None else True
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
    category: Optional[int] = Query(None, description="Filter by category ID"),
    is_published: Optional[bool] = Query(True, description="Filter by publication status")
):
    logger.info(f"Retrieving posts with skip={skip}, limit={limit}, category={category}, is_published={is_published}")
    
    # Build filter dict for MongoDB query
    filters = {}
    if category is not None:
        filters["categories"] = category
    if is_published is not None:
        filters["is_published"] = is_published
    
    # Determine sort direction
    sort_direction = -1 if order.lower() == "desc" else 1
    
    posts = crud.get_filtered_posts(
        skip=skip, 
        limit=limit, 
        filters=filters, 
        sort_by=sort_by, 
        sort_direction=sort_direction
    )
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
    post_data: schemas.PostUpdateRequest,
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
        
    # Update post with only provided fields
    updates = {"updated_at": datetime.now(timezone.utc)}
    
    if post_data.title is not None:
        updates["title"] = post_data.title
    if post_data.content is not None:
        updates["content"] = post_data.content
    if post_data.categories is not None:
        updates["categories"] = post_data.categories
    if post_data.is_published is not None:
        updates["is_published"] = post_data.is_published
    
    crud.update_post(post_id, updates)
    
    # Get updated post
    updated_post = crud.get_post_by_id(post_id)
    logger.info(f"Post updated: {post_id}")
    return updated_post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
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
    # Return nothing for 204 No Content

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

@router.post("/{post_id}/images", response_model=schemas.ImageResponse)
async def upload_post_image(
    post_id: str,
    file: UploadFile = File(...),
    current_user: UserModel = Depends(auth.get_current_user)
):
    logger.info(f"Image upload requested for post ID: {post_id}")
    
    # Check if post exists
    existing_post = crud.get_post_by_id(post_id)
    if not existing_post:
        logger.warning(f"Post not found with ID: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")
        
    # Check if user is the author
    if existing_post.author_id != str(current_user.id) and not current_user.is_admin:
        logger.warning(f"Unauthorized image upload attempt by user: {current_user.email}")
        raise HTTPException(status_code=403, detail="You can only upload images to your own posts")
    
    # Create a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Ensure the uploads directory exists
    os.makedirs("uploads/images", exist_ok=True)
    
    # Save the file
    file_path = f"uploads/images/{unique_filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Store the image reference in the database
    # This is a simplified implementation - in a real app you'd store this in MongoDB
    image_id = str(uuid.uuid4())
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    image_url = f"{base_url}/{file_path}"
    
    logger.info(f"Image uploaded successfully: {unique_filename}")
    
    return schemas.ImageResponse(
        id=image_id,
        filename=unique_filename,
        url=image_url
    )

# Comment endpoints
@router.get("/{post_id}/comments", response_model=List[schemas.CommentResponse])
async def get_post_comments(
    post_id: str,
    skip: int = Query(0, description="Number of comments to skip", alias="page"),
    limit: int = Query(10, description="Maximum number of comments to return")
):
    logger.info(f"Retrieving comments for post ID: {post_id}")
    
    # Check if post exists
    post = crud.get_post_by_id(post_id)
    if not post:
        logger.warning(f"Post not found with ID: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Get comments for post
    comments = crud.get_comments_for_post(post_id)
    
    # Apply pagination
    paginated_comments = comments[skip:skip+limit] if comments else []
    
    # Convert to CommentResponse objects
    response_comments = []
    for comment in paginated_comments:
        response_comments.append(schemas.CommentResponse(
            id=str(comment["_id"]),
            post_id=post_id,
            author_id=comment["author_id"],
            content=comment["content"],
            parent_id=comment.get("parent_id"),
            created_at=comment["created_at"],
            updated_at=comment.get("updated_at"),
            is_published=comment.get("is_published", True)
        ))
    
    logger.info(f"Returning {len(response_comments)} comments for post: {post_id}")
    return response_comments

@router.post("/{post_id}/comments", response_model=schemas.CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_post_comment(
    post_id: str,
    comment_data: schemas.CommentCreate,
    current_user: UserModel = Depends(auth.get_current_user)
):
    logger.debug(f">>>>>Creating comment for post ID: {post_id} by user: {current_user.email}")
    
    # Check if post exists
    post = crud.get_post_by_id(post_id)
    if not post:
        logger.warning(f"Post not found with ID: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if parent comment exists (if specified)
    if comment_data.parent_id:
        # Find parent comment
        comments = crud.get_comments_for_post(post_id)
        parent_comment = next((c for c in comments if str(c["_id"]) == comment_data.parent_id), None)
        
        if not parent_comment:
            logger.warning(f"Parent comment not found with ID: {comment_data.parent_id}")
            raise HTTPException(status_code=404, detail="Parent comment not found")
    
    # Create comment object with a new ObjectId
    comment_id = ObjectId()
    comment = {
        "_id": comment_id,
        "author_id": str(current_user.id),
        "content": comment_data.content,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "is_published": True
    }
    
    # Add parent_id if specified
    if comment_data.parent_id:
        comment["parent_id"] = comment_data.parent_id
    
    logger.debug(f">>>>>Comment data before saving to database: {comment}")

    # Save comment to database
    result = crud.create_comment(post_id, comment)
    
    logger.debug(f">>>>>Created comment result: {result}")

    if not result or result.modified_count == 0:
        logger.error(f"Failed to create comment for post: {post_id}")
        raise HTTPException(status_code=500, detail="Failed to create comment")
    
    logger.debug(f">>>>>Comment created for post: {post_id}")
    
    # Return the created comment as a CommentResponse object
    return schemas.CommentResponse(
        id=str(comment_id),
        post_id=post_id,
        author_id=comment["author_id"],
        content=comment["content"],
        parent_id=comment.get("parent_id"),
        created_at=comment["created_at"],
        updated_at=comment.get("updated_at"),
        is_published=comment.get("is_published", True)
    )
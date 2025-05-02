from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File

from app.routers.utils import store_image_reference
from .. import auth, crud, schemas
from ..models import UserModel, PostModel, CommentModel
from datetime import datetime, timezone
from ..logger import get_logger
from typing import List, Optional
import os
import uuid
from bson.objectid import ObjectId
from ..object_storage import get_minio_client, get_file_url
import io

logger = get_logger(__name__)

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)

@router.post("", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: schemas.PostCreateRequest,
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
    
    # Read file content
    content = await file.read()
    
    # Set the bucket name - assuming a standard bucket for images
    bucket_name = "blog-images"
    
    # Get the Minio client
    minio_client = get_minio_client()
    
    # Make sure the bucket exists
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            logger.info(f"Created bucket: {bucket_name}")
    except Exception as e:
        logger.error(f"Failed to create or check bucket: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to prepare storage")
    
    # Upload file to S3/Minio
    object_name = f"posts/{post_id}/images/{unique_filename}"
    try:
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=io.BytesIO(content),
            length=len(content),
            content_type=file.content_type
        )
        logger.info(f"File uploaded to S3: {object_name}")
    except Exception as e:
        logger.error(f"Failed to upload file to S3: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload image")
    
    # Generate a URL for the uploaded file
    try:
        image_url = minio_client.presigned_get_object(
            bucket_name=bucket_name,
            object_name=object_name,
            expires=7*24*60*60  # URL valid for 7 days
        )
    except Exception as e:
        logger.error(f"Failed to generate URL for uploaded file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate image URL")
    
    # Create image reference in database
    image_id = str(ObjectId())
    image_data = {
        "_id": ObjectId(image_id),
        "filename": unique_filename,
        "object_name": object_name,
        "bucket_name": bucket_name,
        "content_type": file.content_type,
        "post_id": post_id,
        "author_id": str(current_user.id),
        "upload_date": datetime.now(timezone.utc)
    }
    
    # Store the image reference in the database
    try:
        # Assuming crud has a method to store image references
        crud.create_image_reference(image_data)
        logger.info(f"Image reference stored in database with ID: {image_id}")
    except Exception as e:
        logger.error(f"Failed to store image reference: {str(e)}")
        # We won't raise an exception here since the file is already uploaded
    
    logger.info(f"Image uploaded successfully: {unique_filename}")
    
    return schemas.ImageResponse(
        id=image_id,
        filename=unique_filename,
        url=image_url
    )

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
    
    # Get comments for post from separate collection
    comments = crud.get_comments_for_post_v2(post_id, limit=limit, skip=skip)
    
    logger.info(f"Returning {len(comments)} comments for post: {post_id}")
    return comments

@router.post("/{post_id}/comments", response_model=schemas.CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_post_comment(
    post_id: str,
    comment_data: schemas.CommentCreateRequest,
    current_user: UserModel = Depends(auth.get_current_user)
):
    logger.info(f"Creating comment for post ID: {post_id} by user: {current_user.email}")
    
    # Check if post exists
    post = crud.get_post_by_id(post_id)
    if not post:
        logger.warning(f"Post not found with ID: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if parent comment exists (if specified)
    if comment_data.parent_id:
        parent_comment = crud.get_comment_by_id(comment_data.parent_id)
        
        if not parent_comment:
            logger.warning(f"Parent comment not found with ID: {comment_data.parent_id}")
            raise HTTPException(status_code=404, detail="Parent comment not found")
        
        # Ensure parent comment belongs to this post
        if parent_comment.post_id != post_id:
            logger.warning(f"Parent comment {comment_data.parent_id} does not belong to post {post_id}")
            raise HTTPException(status_code=400, detail="Parent comment does not belong to this post")
    
    # Create a new comment model
    comment = CommentModel(
        post_id=post_id,
        author_id=str(current_user.id),
        content=comment_data.content,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        parent_id=comment_data.parent_id,
        is_published=True
    )
    
    # Save comment to separate comments collection
    created_comment = crud.create_comment_v2(comment)
    
    logger.info(f"Comment created for post: {post_id} with ID: {created_comment.id}")
    return created_comment
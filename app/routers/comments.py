from fastapi import APIRouter, Depends, HTTPException, Query, status
from .. import auth, crud, schemas
from ..models import UserModel, CommentModel
from datetime import datetime, timezone
from ..logger import get_logger
from typing import List, Optional
from bson.objectid import ObjectId

logger = get_logger(__name__)

router = APIRouter(
    prefix="/comments",
    tags=["comments"],
)

# GET /comments/{comment_id}
@router.get("/{comment_id}", response_model=schemas.CommentResponse)
async def get_comment(
    comment_id: str
):
    logger.info(f"Retrieving comment with ID: {comment_id}")
    
    comment = crud.get_comment_by_id(comment_id)
    
    if not comment:
        logger.warning(f"Comment not found with ID: {comment_id}")
        raise HTTPException(status_code=404, detail="Comment not found")
    
    logger.info(f"Comment retrieved: {comment_id}")
    return comment

# PUT /comments/{comment_id}
@router.put("/{comment_id}", response_model=schemas.CommentResponse)
async def update_comment(
    comment_id: str,
    comment_data: schemas.CommentUpdateRequest,
    current_user: UserModel = Depends(auth.get_current_user)
):
    logger.info(f"Updating comment with ID: {comment_id}")
    
    # Get the comment
    comment = crud.get_comment_by_id(comment_id)
    
    if not comment:
        logger.warning(f"Comment not found with ID: {comment_id}")
        raise HTTPException(status_code=404, detail="Comment not found")
        
    # Check if user is the author or admin
    if comment.author_id != str(current_user.id) and not current_user.is_admin:
        logger.warning(f"Unauthorized update attempt by user: {current_user.email}")
        raise HTTPException(status_code=403, detail="You can only update your own comments")
    
    # Update comment with only provided fields
    updates = {}
    updates["updated_at"] = datetime.now(timezone.utc)
    
    if comment_data.body is not None:
        updates["body"] = comment_data.body
    
    # Optional fields
    if comment_data.is_published is not None:
        updates["is_published"] = comment_data.is_published
    
    # Update the comment in the database
    crud.update_comment_v2(comment_id, updates)
    
    # Get updated comment
    updated_comment = crud.get_comment_by_id(comment_id)
    
    if not updated_comment:
        logger.error(f"Failed to retrieve updated comment: {comment_id}")
        raise HTTPException(status_code=500, detail="Failed to update comment")
    
    logger.info(f"Comment updated: {comment_id}")
    return updated_comment

# DELETE /comments/{comment_id}
@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    current_user: UserModel = Depends(auth.get_current_user)
):
    logger.info(f"Deleting comment with ID: {comment_id}")
    
    # Get the comment
    comment = crud.get_comment_by_id(comment_id)
    
    if not comment:
        logger.warning(f"Comment not found with ID: {comment_id}")
        raise HTTPException(status_code=404, detail="Comment not found")
        
    # Check if user is the author or admin
    if comment.author_id != str(current_user.id) and not current_user.is_admin:
        logger.warning(f"Unauthorized delete attempt by user: {current_user.email}")
        raise HTTPException(status_code=403, detail="You can only delete your own comments")
    
    # Delete the comment
    crud.delete_comment_v2(comment_id)
    logger.info(f"Comment deleted: {comment_id}")
    # Return nothing for 204 No Content


# POST /comments/{comment_id}/replies
@router.post("/{comment_id}/replies", response_model=schemas.CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment_reply(
    comment_id: str,
    comment_data: schemas.CommentCreateRequest,
    current_user: UserModel = Depends(auth.get_current_user)
):
    logger.info(f"Creating reply for comment ID: {comment_id}")
    
    # Check if parent comment exists
    parent_comment = crud.get_comment_by_id(comment_id)
    
    if not parent_comment:
        logger.warning(f"Parent comment not found with ID: {comment_id}")
        raise HTTPException(status_code=404, detail="Parent comment not found")
    
    # Create a new comment model with parent_id
    comment = CommentModel(
        body=comment_data.body,
        post_id=parent_comment.post_id,  # Use the same post_id as parent
        author_id=str(current_user.id),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        parent_id=comment_id,  # Set parent_id to the comment being replied to
        is_published=True
    )
    
    # Save comment to database
    created_comment = crud.create_comment_v2(comment)
    
    logger.info(f"Reply created for comment: {comment_id}")
    return created_comment
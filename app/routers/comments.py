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

# GET /api/v1/posts/{post_id}/comments
# This endpoint is defined in a separate router that will be included in routes.py

# PUT /api/v1/comments/{comment_id}
@router.put("/{comment_id}", response_model=schemas.CommentResponse)
async def update_comment(
    comment_id: str,
    comment_data: schemas.CommentUpdateRequest,
    current_user: UserModel = Depends(auth.get_current_user)
):
    logger.info(f"Updating comment with ID: {comment_id}")
    
    # The CRUD operations store comments inside posts, so we need to find which post contains the comment
    # This would be more efficient with a separate comments collection
    posts = crud.posts_collection.find({"comments._id": ObjectId(comment_id)})
    post = next((p for p in posts), None)
    
    if not post:
        logger.warning(f"Comment not found with ID: {comment_id}")
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Find the comment in the post
    comment = next((c for c in post.get("comments", []) if str(c["_id"]) == comment_id), None)
    
    if not comment:
        logger.warning(f"Comment not found with ID: {comment_id}")
        raise HTTPException(status_code=404, detail="Comment not found")
        
    # Check if user is the author or admin
    if comment["author_id"] != str(current_user.id) and not current_user.is_admin:
        logger.warning(f"Unauthorized update attempt by user: {current_user.email}")
        raise HTTPException(status_code=403, detail="You can only update your own comments")
    
    # Update comment with only provided fields
    updates = comment.copy()
    updates["updated_at"] = datetime.now(timezone.utc)
    
    if comment_data.content is not None:
        updates["content"] = comment_data.content
    
    # Optional fields
    if comment_data.is_published is not None:
        updates["is_published"] = comment_data.is_published
    
    # Update the comment in the database
    crud.update_comment(str(post["_id"]), comment_id, updates)
    
    # Get updated comment
    post = crud.posts_collection.find_one({"comments._id": ObjectId(comment_id)})
    updated_comment = next((c for c in post.get("comments", []) if str(c["_id"]) == comment_id), None)
    
    if not updated_comment:
        logger.error(f"Failed to retrieve updated comment: {comment_id}")
        raise HTTPException(status_code=500, detail="Failed to update comment")
    
    logger.info(f"Comment updated: {comment_id}")
    
    # Convert to CommentResponse
    return schemas.CommentResponse(
        id=str(updated_comment["_id"]),
        post_id=str(post["_id"]),
        author_id=updated_comment["author_id"],
        content=updated_comment["content"],
        parent_id=updated_comment.get("parent_id"),
        created_at=updated_comment["created_at"],
        updated_at=updated_comment.get("updated_at"),
        is_published=updated_comment.get("is_published", True)
    )

# DELETE /api/v1/comments/{comment_id}
@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    current_user: UserModel = Depends(auth.get_current_user)
):
    logger.info(f"Deleting comment with ID: {comment_id}")
    
    # Find which post contains the comment
    posts = crud.posts_collection.find({"comments._id": ObjectId(comment_id)})
    post = next((p for p in posts), None)
    
    if not post:
        logger.warning(f"Comment not found with ID: {comment_id}")
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Find the comment in the post
    comment = next((c for c in post.get("comments", []) if str(c["_id"]) == comment_id), None)
    
    if not comment:
        logger.warning(f"Comment not found with ID: {comment_id}")
        raise HTTPException(status_code=404, detail="Comment not found")
        
    # Check if user is the author or admin
    if comment["author_id"] != str(current_user.id) and not current_user.is_admin:
        logger.warning(f"Unauthorized delete attempt by user: {current_user.email}")
        raise HTTPException(status_code=403, detail="You can only delete your own comments")
    
    # Delete the comment
    crud.delete_comment(str(post["_id"]), comment_id)
    logger.info(f"Comment deleted: {comment_id}")
    # Return nothing for 204 No Content
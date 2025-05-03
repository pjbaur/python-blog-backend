from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from enum import Enum
from .. import crud, schemas
from ..logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/search",
    tags=["search"]
)

class SearchType(str, Enum):
    """Enum for search type options"""
    POSTS = "posts"
    COMMENTS = "comments"
    ALL = "all"

@router.get("", response_model=schemas.SearchResponse)
async def search(
    q: str = Query(..., description="Search query"),
    page: int = Query(0, description="Page number (pagination)"),
    limit: int = Query(10, description="Maximum number of results to return"),
    type: SearchType = Query(SearchType.ALL, description="Type of content to search"),
    sort_by: str = Query("relevance", description="Field to sort by (relevance, created_at)")
):
    """
    Perform a full-text search across posts and comments.
    
    This endpoint allows searching for content in the blog by keyword.
    Results can be filtered by type (posts, comments, or all).
    
    Args:
        q: The search query
        page: Page number for pagination (0-based)
        limit: Maximum number of results per page
        type: Type of content to search (posts, comments, or all)
        sort_by: Field to sort results by (relevance or created_at)
    
    Returns:
        SearchResponse object containing search results and pagination metadata
    """
    logger.info(f"Search request with query: '{q}', type: {type}, page: {page}, limit: {limit}")
    
    # Initialize variables for result collection
    results = []
    total_results = 0
    
    # Validate sort field and determine direction
    sort_direction = -1  # Default to descending
    if sort_by not in ["relevance", "created_at"]:
        sort_by = "relevance"
    
    # Search posts if requested
    if type in [SearchType.POSTS, SearchType.ALL]:
        # Calculate how many results to fetch based on the requested type
        fetch_limit = limit if type == SearchType.POSTS else limit // 2
        
        # Get post search results
        try:
            posts = crud.search_posts_v2(
                query=q,
                limit=fetch_limit,
                skip=page * fetch_limit if type == SearchType.POSTS else 0,
                sort_by=sort_by,
                sort_direction=sort_direction
            )
            
            # Convert posts to search result items
            for post in posts:
                # Create a search result item from the post
                search_item = schemas.SearchPostResult(
                    id=post.id,
                    type="post",
                    title=post.title,
                    body_preview=getattr(post, 'body_preview', post.body[:200] + "..." if len(post.body) > 200 else post.body),
                    author_id=post.author_id,
                    created_at=post.created_at,
                    updated_at=post.updated_at,
                    post_id=post.id
                )
                results.append(search_item)
                
            logger.info(f"Found {len(posts)} posts matching query '{q}'")
            
            # If we're only searching posts, update the total count
            if type == SearchType.POSTS:
                # For accurate pagination, we'd need to get total count without limit
                # This is a simplified approach
                total_results = len(posts)
                
        except Exception as e:
            logger.error(f"Error searching posts: {str(e)}")
            raise HTTPException(status_code=500, detail="Error performing search on posts")
    
    # Search comments if requested
    if type in [SearchType.COMMENTS, SearchType.ALL]:
        # Calculate how many results to fetch based on the requested type
        fetch_limit = limit if type == SearchType.COMMENTS else limit // 2
        
        # Get comment search results
        try:
            comments = crud.search_comments(
                query=q,
                limit=fetch_limit,
                skip=page * fetch_limit if type == SearchType.COMMENTS else 0,
                sort_by=sort_by,
                sort_direction=sort_direction
            )
            
            # Convert comments to search result items
            for comment in comments:
                # Create a search result item from the comment
                search_item = schemas.SearchCommentResult(
                    id=comment.id,
                    type="comment",
                    body_preview=getattr(comment, 'body_preview', comment.body[:200] + "..." if len(comment.body) > 200 else comment.body),
                    author_id=comment.author_id,
                    created_at=comment.created_at,
                    updated_at=comment.updated_at,
                    post_id=comment.post_id
                )
                results.append(search_item)
                
            logger.info(f"Found {len(comments)} comments matching query '{q}'")
            
            # If we're only searching comments, update the total count
            if type == SearchType.COMMENTS:
                # For accurate pagination, we'd need to get total count without limit
                # This is a simplified approach
                total_results = len(comments)
                
        except Exception as e:
            logger.error(f"Error searching comments: {str(e)}")
            raise HTTPException(status_code=500, detail="Error performing search on comments")
    
    # For combined searches, update the total results count
    if type == SearchType.ALL:
        total_results = len(results)
        
        # Sort mixed results by created_at if requested
        if sort_by == "created_at":
            results.sort(key=lambda x: x.created_at, reverse=(sort_direction == -1))
    
    # Prepare the response
    response = schemas.SearchResponse(
        total=total_results,
        page=page,
        limit=limit,
        results=results
    )
    
    logger.info(f"Returning {len(results)} search results for query '{q}'")
    return response
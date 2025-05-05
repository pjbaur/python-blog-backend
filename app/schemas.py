from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    """Base schema for user-related operations.
    
    This schema is used for user registration and user update operations.
    It contains the common fields that are required for these operations."""
    email: EmailStr

class UserCreateRequest(UserBase):
    """Schema for user registration.
    
    This schema is used to parse the request body for user registration.
    It contains the required fields for creating a new user."""
    password: str

class UserUpdate(BaseModel):
    """Schema for user update.

    This schema is used to parse the request body for user update.
    It contains the optional fields that can be updated for an existing user."""
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    """Schema for user response.

    This schema is used to parse the response body for user-related operations.
    It contains the fields that are returned in the response for user-related operations."""
    id: str
    is_active: bool
    is_admin: bool
    tokens: Optional[List[str]] = None

    class Config:
        orm_mode = True

class UserPublicResponse(BaseModel):
    """Schema for public user response.
    
    This schema is used to parse the response body for public user-related operations.
    It contains the fields that are returned in the response for public user-related operations."""
    id: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

# Login Schema

class LoginRequest(BaseModel):
    """Schema for user login.
    
    This schema is used to parse the request body for user login.
    It contains the required fields for user authentication."""
    email: EmailStr
    password: str

# Password Change Schema
class PasswordChangeRequest(BaseModel):
    """Schema for password change.
    
    This schema is used to parse the request body for changing a user's password.
    It contains the required fields for verifying the current password and setting a new one."""
    current_password: str
    new_password: str
    confirm_password: str

# Token Schemas

class TokenInfo(BaseModel):
    """Schema for storing token information.
    
    See Also: app/models.py::TokenInfo
    
    Can this be used for both access and refresh tokens?
    Should I have different schemas for access and refresh tokens?"""
    token: str
    expires_at: datetime

class TokenResponse(BaseModel):
    """ Schema for the token response from the authentication endpoint.
    This schema is used to parse the response from the authentication endpoint
    and extract the access token, refresh token, and token type.
    
    TODO: Read-up on JWTs.
    """
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str

class RefreshTokenRequest(BaseModel):
    """Schema for refreshing the access token.
    
    This schema is used to parse the request body for refreshing the access token.
    It contains the required fields for refreshing the access token."""
    refresh_token: str

class LogoutRequest(BaseModel):
    """Schema for user logout.

    This schema is used to parse the request body for user logout.
    It contains the required fields for user logout."""
    refresh_token: str
    access_token: Optional[str] = None

class TokenVerifyRequest(BaseModel):
    """Schema for token verification.
    
    This schema is used to parse the request body for token verification.
    It contains the token to be verified."""
    token: str

class TokenVerifyResponse(BaseModel):
    """Schema for token verification response.
    
    This schema is used to format the response body for token verification.
    It contains information about the token's validity and the user ID if valid."""
    is_valid: bool
    user_id: Optional[str] = None
    token_type: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# Post Schemas
class PostCreateRequest(BaseModel):
    """Schema for creating a new blog post.
    
    This schema is used to parse the request body for post creation.
    It contains the required and optional fields for creating a new blog post."""
    title: str
    body: str
    categories: Optional[List[int]] = None
    is_published: Optional[bool] = True

class PostResponse(BaseModel):
    """Schema for post response.
    
    This schema is used to format the response body for post-related operations.
    It contains all fields that are returned in the response for a blog post."""
    id: str
    title: str
    body: str
    author_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    categories: Optional[List[int]] = None
    is_published: Optional[bool] = True
    
    class Config:
        orm_mode = True

class PostUpdateRequest(BaseModel):
    """Schema for updating an existing blog post.
    
    This schema is used to parse the request body for post updates.
    It contains optional fields that can be updated for an existing post."""
    title: Optional[str] = None
    body: Optional[str] = None
    categories: Optional[List[int]] = None
    is_published: Optional[bool] = None

# Comment Schemas
class CommentCreateRequest(BaseModel):
    """Schema for creating a new comment.
    
    This schema is used to parse the request body for comment creation.
    It contains the required body field and optional parent_id for nested comments.
    
    The assumption is made that the post_id is passed in the URL path and not in the request body.
    
    TODO: Add a field for comment type (e.g., text, image, video).
    TODO: Add a field for comment status (e.g., approved, spam, deleted).
    TODO: Add validation rules for comment body length and format."""
    body: str
    parent_id: Optional[str] = None

class CommentResponse(BaseModel):
    """Schema for comment response.
    
    This schema is used to format the response body for comment-related operations.
    It contains all fields that are returned in the response for a comment."""
    id: str
    post_id: str
    author_id: str
    body: str
    parent_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_published: bool = True
    # is_edited: bool = False
    # is_deleted: bool = False
    # is_approved: bool = False
    # is_spam: bool = False

    class Config:
        orm_mode = True

class CommentUpdateRequest(BaseModel):
    """Schema for updating an existing comment.
    
    This schema is used to parse the request body for comment updates.
    It contains optional fields that can be updated for an existing comment."""
    body: Optional[str] = None
    parent_id: Optional[str] = None
    is_published: Optional[bool] = None
    # is_edited: Optional[bool] = None
    # is_deleted: Optional[bool] = None
    # is_approved: Optional[bool] = None
    # is_spam: Optional[bool] = None
    # is_flagged: Optional[bool] = None
    # is_archived: Optional[bool] = None
    # is_hidden: Optional[bool] = None

# Image Schemas
class ImageCreateRequest(BaseModel):
    """Schema for creating a new image reference.
    
    This schema is used to parse the request body for image reference creation.
    It contains the required fields for storing information about an uploaded image."""
    filename: str
    filepath: str
    url: str
    uploaded_by: str
    file_size: int
    content_type: str

class ImageResponse(BaseModel):
    """Schema for image response.
    
    This schema is used to format the response body for image-related operations.
    It contains the fields that are returned in the response for an uploaded image."""
    id: str
    filename: str
    url: str
    uploaded_by: str
    upload_date: datetime
    file_size: int
    content_type: str
    
    class Config:
        orm_mode = True

# Search Schemas
class SearchItem(BaseModel):
    """Base schema for search results.
    
    This schema is used to represent a single search result item.
    It contains the common fields that are returned for any type of search result."""
    id: str
    type: str  # "post" or "comment"
    created_at: datetime
    updated_at: Optional[datetime] = None
    body_preview: str
    author_id: str
    
    class Config:
        orm_mode = True

class SearchPostResult(SearchItem):
    """Schema for post search results.
    
    This schema extends the base SearchItem with post-specific fields."""
    title: str
    post_id: Optional[str] = None  # This will be the same as id for posts
    
    class Config:
        orm_mode = True

class SearchCommentResult(SearchItem):
    """Schema for comment search results.
    
    This schema extends the base SearchItem with comment-specific fields."""
    post_id: str
    
    class Config:
        orm_mode = True

class SearchResponse(BaseModel):
    """Schema for search response.
    
    This schema is used to format the response body for search operations.
    It contains metadata about the search and an array of search results."""
    total: int
    page: int
    limit: int
    results: List[SearchItem]
    
    class Config:
        orm_mode = True

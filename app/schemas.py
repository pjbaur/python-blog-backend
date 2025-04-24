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

# Post Schemas
class PostCreateRequest(BaseModel):
    """Schema for creating a new blog post.
    
    This schema is used to parse the request body for post creation.
    It contains the required and optional fields for creating a new blog post."""
    title: str
    content: str
    categories: Optional[List[int]] = None
    is_published: Optional[bool] = True

class PostResponse(BaseModel):
    """Schema for post response.
    
    This schema is used to format the response body for post-related operations.
    It contains all fields that are returned in the response for a blog post."""
    id: str
    title: str
    content: str
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
    content: Optional[str] = None
    categories: Optional[List[int]] = None
    is_published: Optional[bool] = None

# Comment Schemas
class CommentCreateRequest(BaseModel):
    """Schema for creating a new comment.
    
    This schema is used to parse the request body for comment creation.
    It contains the required content field and optional parent_id for nested comments."""
    content: str
    parent_id: Optional[str] = None

class CommentResponse(BaseModel):
    """Schema for comment response.
    
    This schema is used to format the response body for comment-related operations.
    It contains all fields that are returned in the response for a comment."""
    id: str
    post_id: str
    author_id: str
    content: str
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
    content: Optional[str] = None
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
class ImageResponse(BaseModel):
    """Schema for image response.
    
    This schema is used to format the response body for image-related operations.
    It contains the fields that are returned in the response for an uploaded image."""
    id: str
    filename: str
    url: str
    
    class Config:
        orm_mode = True

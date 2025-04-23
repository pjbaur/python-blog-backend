from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None

# Token Info Schema
class TokenInfo(BaseModel):
    """Schema for storing token information.
    
    See Also: app/models.py::TokenInfo
    
    Can this be used for both access and refresh tokens?
    Should I have different schemas for access and refresh tokens?"""
    token: str
    expires_at: datetime

class UserResponse(UserBase):
    id: str
    is_active: bool
    is_admin: bool
    tokens: Optional[List[str]] = None

    class Config:
        orm_mode = True

class UserPublicResponse(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

# Login Schema
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Token Schemas
class Token(BaseModel):
    """ Schema for the token response from the authentication endpoint.
    This schema is used to parse the response from the authentication endpoint
    and extract the access token, refresh token, and token type.
    
    If access and refresh tokens are not interchangable, then this schema should not exist.
    TODO: Read-up on JWTs.
    """
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str
    access_token: Optional[str] = None

# Post Schemas
class PostCreate(BaseModel):
    title: str
    content: str
    categories: Optional[List[int]] = None
    is_published: Optional[bool] = True

class PostResponse(BaseModel):
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
    title: Optional[str] = None
    content: Optional[str] = None
    categories: Optional[List[int]] = None
    is_published: Optional[bool] = None

# Comment Schemas
class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[str] = None

class CommentResponse(BaseModel):
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
    # is_flagged: bool = False
    # is_archived: bool = False
    # is_hidden: bool = False

    class Config:
        orm_mode = True

class CommentUpdateRequest(BaseModel):
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
    id: str
    filename: str
    url: str
    
    class Config:
        orm_mode = True

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
    token: str
    expires_at: datetime

class UserResponse(UserBase):
    id: str
    is_active: bool
    is_admin: bool
    tokens: Optional[List[TokenInfo]] = None

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
    access_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

# Post Schemas
class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: str
    title: str
    content: str
    author_id: str
    created_at: datetime

    class Config:
        orm_mode = True

# Comment Schemas
class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[str] = None

class CommentResponse(BaseModel):
    id: str
    post_id: str
    author_id: str
    content: str
    parent_id: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

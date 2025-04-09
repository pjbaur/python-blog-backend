from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    is_active: bool
    is_admin: bool

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

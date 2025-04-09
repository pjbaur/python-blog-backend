from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone

class UserModel(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    username: str
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    is_admin: bool = False
    tokens: List[str] = []

class PostModel(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    title: str
    content: str
    author_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommentModel(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    post_id: str
    author_id: str
    content: str
    parent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr, Field, BeforeValidator
from datetime import datetime
from typing_extensions import Annotated
from bson.objectid import ObjectId

# Define a callable function to convert ObjectId to string
def object_id_to_str(v: Any) -> str:
    if isinstance(v, ObjectId):
        return str(v)
    return v

# Use Annotated for the id field with BeforeValidator
ObjectIdStr = Annotated[str, BeforeValidator(object_id_to_str)]

class TokenInfo(BaseModel):
    """Model for storing token information.
    
    This model is used to store both access and refresh tokens.
    
    Attributes:
        token (str): The token string.
        expires_at (datetime): The expiration time of the token.

    Who uses this?
        UserModel::tokens
    """
    token: str
    expires_at: datetime

class UserModel(BaseModel):
    id: Optional[ObjectIdStr] = Field(None, alias='_id')
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    is_admin: bool = False
    tokens: List[str] = []

class PostModel(BaseModel):
    id: Optional[ObjectIdStr] = Field(None, alias='_id')
    title: str
    content: str
    author_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommentModel(BaseModel):
    id: Optional[ObjectIdStr] = Field(None, alias='_id')
    post_id: str
    author_id: str
    content: str
    parent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

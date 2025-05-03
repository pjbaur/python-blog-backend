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
    updated_at: Optional[datetime] = None
    is_active: bool = True
    is_admin: bool = False
    tokens: List[str] = []
    password_history: List[str] = []

class PostModel(BaseModel):
    id: Optional[ObjectIdStr] = Field(None, alias='_id')
    title: str
    body: str  # Changed from "content" to "body" to match database schema
    author_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    categories: List[int] = []
    is_published: bool = True
    body_preview: Optional[str] = None

class CommentModel(BaseModel):
    id: Optional[ObjectIdStr] = Field(None, alias='_id')
    post_id: str
    author_id: str
    body: str
    parent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_published: bool = True
    is_deleted: bool = False
    body_preview: Optional[str] = None

class ImageModel(BaseModel):
    """Model for storing image references.
    
    This model is used to store information about uploaded images,
    including their filenames and storage locations.
    
    Attributes:
        id (ObjectIdStr): The unique identifier for the image.
        filename (str): The original filename of the image.
        filepath (str): The path where the image is stored.
        url (str): The URL to access the image.
        uploaded_by (str): The ID of the user who uploaded the image.
        upload_date (datetime): The date and time when the image was uploaded.
        file_size (int): The size of the image file in bytes.
        content_type (str): The MIME type of the image.
    """
    id: Optional[ObjectIdStr] = Field(None, alias='_id')
    filename: str
    filepath: str
    url: str
    uploaded_by: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    file_size: int
    content_type: str

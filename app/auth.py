from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .database import db
from .models import UserModel
from bson.objectid import ObjectId
import os
import dotenv
from .logger import get_logger

# Set up logger
logger = get_logger(__name__)

dotenv.load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

users_collection = db['users']
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_password(plain_password, hashed_password):
    logger.trace("Verifying password")
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    logger.trace("Hashing password")
    return pwd_context.hash(password)

def get_user(email: str):
    logger.debug(f"Fetching user with email: {email}")
    user_data = users_collection.find_one({"email": email})
    if user_data:
        logger.trace(f"User found: {email}")
        return UserModel(**user_data)
    logger.debug(f"User not found: {email}")
    return None

def authenticate_user(email: str, password: str):
    logger.debug(f"Authentication attempt for user: {email}")
    user = get_user(email)
    if not user:
        logger.debug(f"Authentication failed: User not found: {email}")
        return False
    if not verify_password(password, user.hashed_password):
        logger.debug(f"Authentication failed: Invalid password for: {email}")
        return False
    logger.debug(f"User authenticated successfully: {email}")
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "token_type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # Store the token in the user's token list for invalidation
    users_collection.update_one(
        {"_id": ObjectId(data["id"])},
        {"$push": {"tokens": encoded_jwt}}
    )
    logger.debug(f"Access token created for user ID: {data['id']}, expires: {expire}")
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a refresh token for the user."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire, "token_type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # Store the refresh token in the user's token list
    users_collection.update_one(
        {"_id": ObjectId(data["id"])},
        {"$push": {"tokens": encoded_jwt}}
    )
    logger.debug(f"Refresh token created for user ID: {data['id']}, expires: {expire}")
    return encoded_jwt

def create_token_pair(data: dict) -> Tuple[str, str]:
    """Create both access and refresh tokens for a user."""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        data=data,
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data=data,
        expires_delta=refresh_token_expires
    )
    
    logger.info(f"Token pair created for user ID: {data['id']}")
    return access_token, refresh_token

def verify_token(token: str, token_type: str = None):
    """Verify a token and return the payload if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        if user_id is None:
            logger.warning("Token validation failed: Missing user ID in token")
            return None
            
        # Check token type if specified
        if token_type and payload.get("token_type") != token_type:
            logger.warning(f"Token validation failed: Expected {token_type} token but got {payload.get('token_type')}")
            return None
            
        # Check if token exists in user's token list
        user = users_collection.find_one({"_id": ObjectId(user_id), "tokens": token})
        if not user:
            logger.warning(f"Token validation failed: Token not found for user ID: {user_id}")
            return None
            
        logger.debug(f"Token verified successfully for user ID: {user_id}")
        return payload
    except JWTError as e:
        logger.warning(f"Token validation failed: JWT Error: {str(e)}")
        return None

def invalidate_token(token: str):
    """Remove a token from the user's token list."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        if user_id:
            result = users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$pull": {"tokens": token}}
            )
            logger.info(f"Token invalidated for user ID: {user_id}, modified: {result.modified_count}")
            return result.modified_count > 0
    except JWTError as e:
        logger.warning(f"Token invalidation failed: JWT Error: {str(e)}")
    return False

async def get_current_user(token: str = Depends(oauth2_scheme)):
    logger.debug("Validating token for authentication")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token, token_type="access")
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("id")
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    if user_data is None:
        logger.warning(f"User not found with ID: {user_id}")
        raise credentials_exception
    
    logger.debug(f"User authenticated via token: {user_data.get('email')}")
    return UserModel(**user_data)

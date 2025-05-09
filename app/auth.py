from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import jwt
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .database import db
from .models import UserModel, TokenInfo
from bson.objectid import ObjectId
import os
import dotenv
from .logger import get_logger

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
    """Create an access token for the user."""
    logger.debug("Creating access token")
    logger.debug("Data for token: %s", data) # TODO remove in production
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "token_type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # Store the token as a string
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
    # Store the refresh token as a string
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
    
    logger.debug(f"Token pair created for user ID: {data['id']}")
    logger.debug(f"Access token: {access_token}")
    logger.debug(f"Refresh token: {refresh_token}")
    return access_token, refresh_token

def verify_token(token: str, token_type: str = None):
    """Verify a token and return the payload if valid.
    This function checks if the token is valid and if it exists in the user's token list.
    It also checks if the token type matches the expected type (access or refresh).
    If the token is valid, it returns the payload; otherwise, it returns None.
    """
    logger.debug(f"Verifying token: {token}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Token payload: {payload}")

        user_id = payload.get("id")
        logger.debug(f"Verifying token for user ID: {user_id}")
        if user_id is None:
            logger.warning("Token validation failed: Missing user ID in token")
            return None
            
        # Check token type if specified
        if token_type and payload.get("token_type") != token_type:
            logger.warning(f"Token validation failed: Expected {token_type} token but got {payload.get('token_type')}")
            return None
            
        # Check if token exists in user's token list (now in TokenInfo format)
        # Is this checking all tokens in the token field?
        user = users_collection.find_one({"_id": ObjectId(user_id), "tokens": token})
        if not user:
            logger.warning(f"Token validation failed: Token not found for user ID: {user_id}")
            return None
            
        logger.debug(f"Token verified successfully for user ID: {user_id}")
        return payload
    except PyJWTError as e:
        logger.warning(f"Token validation failed: JWT Error: {str(e)}")
        return None

def invalidate_token(token: str):
    """Remove a token from the user's token list."""
    try:
        logger.debug("invalidate_token() -- Invalidating token: %s", token)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")

        # Show the db user before and after the update
        user_before = users_collection.find_one({"_id": ObjectId(user_id)})
        logger.debug(f"User before update: {user_before}")
        if user_id:
            # Try to remove the token in both formats
            # 1. First try to remove as direct token string
            result = users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$pull": {"tokens": token}}
            )
            user_after = users_collection.find_one({"_id": ObjectId(user_id)})
            logger.debug(f"User after update: {user_after}")
            logger.debug(f"Token invalidated for user ID: {user_id}, modified: {result.modified_count}")
            return result.modified_count > 0
    except PyJWTError as e:
        logger.warning(f"Token invalidation failed: JWT Error: {str(e)}")
    return False

def invalidate_tokens(tokens: list):
    """Remove multiple tokens from the user's token list."""
    if not tokens or len(tokens) == 0:
        logger.warning("No tokens provided for invalidation")
        return False
    
    success = True
    for token in tokens:
        if token:  # Skip None or empty tokens
            if not invalidate_token(token):
                success = False
    
    return success

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

def is_jwt_token(token: str) -> bool:
    """Check if the token is a JWT token.
    
    This function only checks if the token has valid JWT format,
    not if it contains the expected payload fields.
    """
    try:
        # Just decode the token to check format, don't verify contents or expiration
        jwt.decode(token, options={"verify_signature": False, "verify_exp": False}, algorithms=[ALGORITHM])
        return True
    except PyJWTError:
        return False
    except Exception as e:
        logger.warning(f"Error checking if token is JWT: {str(e)}")
        return False

def is_token_expired(token: str) -> bool:
    """Check if a token is expired.
    
    Returns:
        bool: True if the token is expired or invalid, False if it is still valid.
    """
    try:
        # Decode the token without verification to get expiry time
        payload = jwt.decode(token, options={"verify_signature": False}, algorithms=[ALGORITHM])
        exp_timestamp = payload.get("exp")
        if not exp_timestamp:
            logger.warning("Token has no expiry date")
            return True
            
        # Check if token has expired
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        logger.debug(f"Token expiry: {exp_datetime}, Current time: {now}")
        return now >= exp_datetime
    except PyJWTError as e:
        logger.warning(f"Token expiry check failed: {str(e)}")
        return True
    except Exception as e:
        logger.warning(f"Error checking token expiry: {str(e)}")
        return True

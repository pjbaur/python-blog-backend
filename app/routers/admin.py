from fastapi import APIRouter, Depends, HTTPException
from .. import auth, crud, schemas
from ..models import UserModel
from datetime import datetime
from ..logger import get_logger

# Set up logger
logger = get_logger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

# Admin: Get All Users
@router.get("/users", response_model=list[schemas.UserResponse])
async def admin_get_users(current_user: UserModel = Depends(auth.get_current_user)):
    logger.info(f"Admin request to get all users from: {current_user.email}")
    if not current_user.is_admin:
        logger.warning(f"Unauthorized admin access attempt by: {current_user.email}")
        raise HTTPException(status_code=403, detail="Not authorized")
    users = crud.get_all_users()
    
    # Process each user to add token expiration info
    for user in users:
        if user.tokens:
            token_info_list = []
            for token in user.tokens:
                try:
                    # Decode the token to get expiration time
                    payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
                    exp_timestamp = payload.get("exp")
                    if exp_timestamp:
                        # Convert unix timestamp to datetime
                        expires_at = datetime.fromtimestamp(exp_timestamp)
                        token_info_list.append(schemas.TokenInfo(token=token, expires_at=expires_at))
                except auth.JWTError:
                    # Skip invalid tokens
                    logger.debug(f"Invalid token found for user: {user.email}")
                    continue
            user.tokens = token_info_list
        else:
            user.tokens = []
    
    logger.info(f"Returning data for {len(users)} users")    
    return users
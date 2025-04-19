from fastapi import APIRouter, Depends, HTTPException
from .. import auth, crud, schemas
from ..models import UserModel
from app.logger import get_logger

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
    
    logger.info(f"Returning data for {len(users)} users")
    logger.debug(f"Type of users: {type(users)}")

    return users
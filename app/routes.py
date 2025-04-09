from fastapi import APIRouter, Depends, HTTPException
from . import auth, crud, schemas
from .models import UserModel
from datetime import timedelta, datetime, timezone
import os

# Make sure we have access to JWTError
from .auth import JWTError

router = APIRouter()

# User Registration
@router.post("/users/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate):
    existing_user = crud.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    user_model = UserModel(
        email=user.email,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=False,
        created_at=datetime.now(timezone.utc)
    )
    return crud.create_user(user_model)

# User Login
@router.post("/auth/login", response_model=schemas.Token)
def login_user(login_data: schemas.LoginRequest):
    user = auth.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"id": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Get Current User
@router.get("/users/me", response_model=schemas.UserResponse)
async def get_current_user(current_user: UserModel = Depends(auth.get_current_user)):
    return current_user

# Admin: Get All Users
@router.get("/admin/users", response_model=list[schemas.UserResponse])
async def admin_get_users(current_user: UserModel = Depends(auth.get_current_user)):
    if not current_user.is_admin:
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
                    continue
            user.tokens = token_info_list
        else:
            user.tokens = []
            
    return users

# Healthcheck endpoint
@router.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}
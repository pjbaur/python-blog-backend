from fastapi import FastAPI, Depends, HTTPException
from . import auth, crud, schemas
from .models import UserModel
from datetime import timedelta
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

app = FastAPI()

# Create initial admin user on startup if it doesn't exist
@app.on_event("startup")
async def create_initial_admin():
    admin_email = os.getenv("INITIAL_ADMIN_EMAIL")
    admin_password = os.getenv("INITIAL_ADMIN_PASSWORD")
    
    if admin_email and admin_password:
        existing_user = crud.get_user_by_email(admin_email)
        if not existing_user:
            hashed_password = auth.get_password_hash(admin_password)
            user_model = UserModel(
                email=admin_email,
                hashed_password=hashed_password,
                is_active=True,
                is_admin=True,
                created_at=datetime.now(timezone.utc)
            )
            crud.create_user(user_model)
            print(f"Initial admin user created with email: {admin_email}")
        else:
            # Ensure the user has admin privileges
            if not existing_user.is_admin or not existing_user.is_active:
                crud.update_user(str(existing_user.id), {"is_admin": True, "is_active": True})
                print(f"Updated user {admin_email} to have admin privileges")

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

# User Registration
@app.post("/users/register", response_model=schemas.UserResponse)
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
@app.post("/auth/login", response_model=schemas.Token)
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
@app.get("/users/me", response_model=schemas.UserResponse)
async def get_current_user(current_user: UserModel = Depends(auth.get_current_user)):
    return current_user

# Admin: Get All Users
@app.get("/admin/users", response_model=list[schemas.UserResponse])
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

# Additional routes for posts and comments would go here...

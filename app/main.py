from fastapi import FastAPI, Depends, HTTPException, status
from . import auth, crud, schemas
from .models import UserModel
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

app = FastAPI()

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
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    return crud.create_user(user_model)

# User Login
@app.post("/auth/login", response_model=schemas.Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(form_data.username, form_data.password)
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
    return users

# Additional routes for posts and comments would go here...

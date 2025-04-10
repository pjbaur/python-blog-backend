from fastapi import FastAPI
from . import auth, crud
from .models import UserModel
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from .routes import router
from .logger import setup_logging, get_logger
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Set up logging
logger = get_logger(__name__)

# Create initial admin user on startup if it doesn't exist
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
            logger.info(f"Initial admin user created with email: {admin_email}")
        else:
            # Ensure the user has admin privileges
            if not existing_user.is_admin or not existing_user.is_active:
                crud.update_user(str(existing_user.id), {"is_admin": True, "is_active": True})
                logger.info(f"Updated user {admin_email} to have admin privileges")
    else:
        logger.warning("Admin credentials not provided in environment variables")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialization code (before serving requests)
    setup_logging()
    logger.info("Application startup: Initializing logging")
    await create_initial_admin()
    
    yield  # This is where the application serves requests
    
    # Cleanup code (after serving requests, before shutdown)
    logger.info("Application shutdown")

app = FastAPI(lifespan=lifespan)

# Include the router
app.include_router(router)

# Additional routes for posts and comments would go here...

from fastapi import APIRouter
from .logger import get_logger
from .routers import auth, users, admin, posts

# Set up logger
logger = get_logger(__name__)

# Create main API router with /api/v1 prefix
router = APIRouter(prefix="/api/v1")

# Healthcheck endpoint - keeping outside the API versioning since it's a system endpoint
@router.get("/healthcheck")
def healthcheck():
    logger.debug("Healthcheck endpoint called")
    return {"status": "ok"}

# Include all the routers
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(admin.router)
router.include_router(posts.router)
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from .logger import get_logger

logger = get_logger(__name__)

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
if not MONGO_URI:
    logger.error("No MONGO_URI found in environment variables")
    raise ValueError("No MONGO_URI found in environment variables")

logger.info(f"Connecting to MongoDB at: {MONGO_URI.split('@')[-1]}")  # Log only the host part for security
try:
    client = MongoClient(MONGO_URI)
    # Test the connection
    client.server_info()
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.critical(f"Failed to connect to MongoDB: {str(e)}")
    raise

db = client['blog_db']
logger.info(f"Using database: blog_db")

# Define collections
users_collection = db['users']
posts_collection = db['posts']
comments_collection = db['comments']
images_collection = db['images']
logger.info("Database collections initialized")

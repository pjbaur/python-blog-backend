from .models import UserModel, PostModel
from .database import db
from bson.objectid import ObjectId
from .logger import get_logger
from typing import List, Dict, Any, Optional
from datetime import timedelta

logger = get_logger(__name__)

users_collection = db['users']
posts_collection = db['posts']

# User CRUD operations
def create_user(user: UserModel):
    # Convert to dict but exclude_unset to avoid sending null _id
    user_dict = user.dict(by_alias=True, exclude_unset=True)
    # Explicitly remove _id if it's None to let MongoDB generate it
    if "_id" in user_dict and user_dict["_id"] is None:
        del user_dict["_id"]
    
    logger.info(f"Creating new user with email: {user.email}")
    try:
        insert_result = users_collection.insert_one(user_dict)
        user.id = str(insert_result.inserted_id)
        logger.info(f"User created with ID: {user.id}")
        return user
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise

def get_user_by_email(email: str):
    logger.debug(f"Retrieving user by email: {email}")
    try:
        user_data = users_collection.find_one({"email": email})
        if user_data:
            logger.debug(f"Found user with email: {email}")
            return UserModel(**user_data)
        logger.debug(f"User not found with email: {email}")
        return None
    except Exception as e:
        logger.error(f"Error retrieving user by email: {str(e)}")
        raise

def get_user_by_id(user_id: str):
    logger.debug(f"Retrieving user by ID: {user_id}")
    try:
        user_data = users_collection.find_one({"_id": ObjectId(user_id)})
        if user_data:
            logger.debug(f"Found user with ID: {user_id}")
            return UserModel(**user_data)
        logger.debug(f"User not found with ID: {user_id}")
        return None
    except Exception as e:
        logger.error(f"Error retrieving user by ID: {str(e)}")
        raise

def get_all_users():
    """
    Retrieve all users from the database.
    This function handles legacy token formats by converting string tokens to TokenInfo objects.
    
    TODO: I want to remove the legacy token format."""
    logger.info("app/crud.py get_all_users()")
    try:
        users = []
        for user_data in users_collection.find():
            logger.debug(f"Found user: {user_data}")
            users.append(UserModel(**user_data))
        return users
    except Exception as e:
        logger.error(f"Error retrieving all users: {str(e)}")
        raise

def update_user(user_id: str, updates: dict):
    logger.info(f"Updating user with ID: {user_id}")
    logger.debug(f"Update data: {updates}")
    try:
        result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
        if result.modified_count > 0:
            logger.info(f"Successfully updated user: {user_id}")
        else:
            logger.warning(f"No changes made to user: {user_id}")
        return result
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise

def delete_user(user_id: str):
    logger.warning(f"Deleting user with ID: {user_id}")
    try:
        result = users_collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count > 0:
            logger.info(f"Successfully deleted user: {user_id}")
        else:
            logger.warning(f"User not found for deletion: {user_id}")
        return result
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise

# Post CRUD operations
def create_post(post: PostModel):
    post_dict = post.dict(by_alias=True, exclude_unset=True)
    if "_id" in post_dict and post_dict["_id"] is None:
        del post_dict["_id"]
    
    logger.info(f"Creating new post with title: {post.title}")
    try:
        insert_result = posts_collection.insert_one(post_dict)
        post.id = str(insert_result.inserted_id)
        logger.info(f"Post created with ID: {post.id}")
        return post
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        raise

def get_post_by_id(post_id: str):
    logger.debug(f"Retrieving post by ID: {post_id}")
    try:
        post_data = posts_collection.find_one({"_id": ObjectId(post_id)})
        if post_data:
            logger.debug(f"Found post with ID: {post_id}")
            return PostModel(**post_data)
        logger.debug(f"Post not found with ID: {post_id}")
        return None
    except Exception as e:
        logger.error(f"Error retrieving post by ID: {str(e)}")
        raise

def get_all_posts(limit: int = 100, skip: int = 0):
    logger.info(f"Retrieving all posts with limit: {limit}, skip: {skip}")
    posts = []
    try:
        for post_data in posts_collection.find().skip(skip).limit(limit).sort("created_at", -1):
            posts.append(PostModel(**post_data))
        logger.info(f"Retrieved {len(posts)} posts")
        return posts
    except Exception as e:
        logger.error(f"Error retrieving all posts: {str(e)}")
        raise

def get_posts_by_author(author_id: str, limit: int = 100, skip: int = 0):
    logger.info(f"Retrieving posts by author ID: {author_id}")
    posts = []
    try:
        for post_data in posts_collection.find({"author_id": author_id}).skip(skip).limit(limit).sort("created_at", -1):
            posts.append(PostModel(**post_data))
        logger.info(f"Retrieved {len(posts)} posts for author: {author_id}")
        return posts
    except Exception as e:
        logger.error(f"Error retrieving posts by author: {str(e)}")
        raise

def update_post(post_id: str, updates: Dict[str, Any]):
    logger.info(f"Updating post with ID: {post_id}")
    logger.debug(f"Update data: {updates}")
    try:
        result = posts_collection.update_one({"_id": ObjectId(post_id)}, {"$set": updates})
        if result.modified_count > 0:
            logger.info(f"Successfully updated post: {post_id}")
        else:
            logger.warning(f"No changes made to post: {post_id}")
        return result
    except Exception as e:
        logger.error(f"Error updating post {post_id}: {str(e)}")
        raise

def delete_post(post_id: str):
    logger.warning(f"Deleting post with ID: {post_id}")
    try:
        result = posts_collection.delete_one({"_id": ObjectId(post_id)})
        if result.deleted_count > 0:
            logger.info(f"Successfully deleted post: {post_id}")
        else:
            logger.warning(f"Post not found for deletion: {post_id}")
        return result
    except Exception as e:
        logger.error(f"Error deleting post {post_id}: {str(e)}")
        raise

def search_posts(query: str, limit: int = 100, skip: int = 0):
    logger.info(f"Searching posts with query: {query}")
    posts = []
    try:
        search_query = {"$text": {"$search": query}}
        for post_data in posts_collection.find(search_query).skip(skip).limit(limit).sort("created_at", -1):
            posts.append(PostModel(**post_data))
        logger.info(f"Found {len(posts)} posts matching search query")
        return posts
    except Exception as e:
        logger.error(f"Error searching posts: {str(e)}")
        raise

def filter_posts(filters: Dict[str, Any], limit: int = 100, skip: int = 0):
    logger.info(f"Filtering posts with filters: {filters}")
    posts = []
    try:
        for post_data in posts_collection.find(filters).skip(skip).limit(limit).sort("created_at", -1):
            posts.append(PostModel(**post_data))
        logger.info(f"Filtered {len(posts)} posts")
        return posts
    except Exception as e:
        logger.error(f"Error filtering posts: {str(e)}")
        raise

def get_filtered_posts(skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None, sort_by: str = "created_at", sort_direction: int = -1):   
    logger.info(f"Retrieving filtered posts with skip: {skip}, limit: {limit}, filters: {filters}, sort_by: {sort_by}, sort_direction: {sort_direction}")
    posts = []
    try:
        query = {}
        if filters:
            query.update(filters)
        for post_data in posts_collection.find(query).skip(skip).limit(limit).sort(sort_by, sort_direction):
            posts.append(PostModel(**post_data))
        logger.info(f"Retrieved {len(posts)} filtered posts")
        return posts
    except Exception as e:
        logger.error(f"Error retrieving filtered posts: {str(e)}")
        raise

def get_posts_by_category(category_id: int, limit: int = 100, skip: int = 0):
    logger.info(f"Retrieving posts by category ID: {category_id}")
    posts = []
    try:
        for post_data in posts_collection.find({"category_id": category_id}).skip(skip).limit(limit).sort("created_at", -1):
            posts.append(PostModel(**post_data))
        logger.info(f"Retrieved {len(posts)} posts for category: {category_id}")
        return posts
    except Exception as e:
        logger.error(f"Error retrieving posts by category: {str(e)}")
        raise

def get_posts_by_author_and_category(author_id: str, category_id: int, limit: int = 100, skip: int = 0):
    logger.info(f"Retrieving posts by author ID: {author_id} and category ID: {category_id}")
    posts = []
    try:
        for post_data in posts_collection.find({"author_id": author_id, "category_id": category_id}).skip(skip).limit(limit).sort("created_at", -1):
            posts.append(PostModel(**post_data))
        logger.info(f"Retrieved {len(posts)} posts for author: {author_id} and category: {category_id}")
        return posts
    except Exception as e:
        logger.error(f"Error retrieving posts by author and category: {str(e)}")
        raise


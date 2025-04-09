from .models import UserModel
from .database import db
from bson.objectid import ObjectId
from .logger import get_logger

# Set up logger
logger = get_logger(__name__)

users_collection = db['users']

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
    logger.info("Retrieving all users")
    users = []
    try:
        for user_data in users_collection.find():
            users.append(UserModel(**user_data))
        logger.info(f"Retrieved {len(users)} users")
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

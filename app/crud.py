from .models import UserModel, PostModel, CommentModel
from .database import db, users_collection, posts_collection, comments_collection
from bson.objectid import ObjectId
from .logger import get_logger
from typing import Dict, Any, Optional
from datetime import timedelta

logger = get_logger(__name__)

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
    """Retrieve all users from the database."""
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
        logger.debug(f"////Post: {post}")
        logger.debug(f"////insert_result: {insert_result}")
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

# Comment CRUD operations
def create_comment(post_id: str, comment: Dict[str, Any]):
    logger.info(f"Creating comment for post ID: {post_id}")
    try:
        comment["post_id"] = post_id
        # This is inserting the comment into the post's comments array!
        # Is this the behavior we want? Sounds good, but need to make sure the rest of the app expects this (including schema and model).
        # The comment should have a unique ID, so we can use ObjectId() to generate one.
        insert_result = posts_collection.update_one({"_id": ObjectId(post_id)}, {"$push": {"comments": comment}})
        if insert_result.modified_count > 0:
            logger.info(f"Comment added to post: {post_id}")
        else:
            logger.warning(f"No changes made to post: {post_id}")
        # Is this what should be returned?
        # UpdateResult({'n': 1, 'nModified': 1, 'ok': 1.0, 'updatedExisting': True}, acknowledged=True)
        logger.debug(f"+++++insert_result: {insert_result}")
        return insert_result
    except Exception as e:
        logger.error(f"Error creating comment for post {post_id}: {str(e)}")
        raise

def get_comments_for_post(post_id: str):
    logger.info(f"Retrieving comments for post ID: {post_id}")
    try:
        post_data = posts_collection.find_one({"_id": ObjectId(post_id)})
        if post_data and "comments" in post_data:
            logger.info(f"Found {len(post_data['comments'])} comments for post: {post_id}")
            return post_data["comments"]
        logger.debug(f"No comments found for post: {post_id}")
        return []
    except Exception as e:
        logger.error(f"Error retrieving comments for post {post_id}: {str(e)}")
        raise

def update_comment(post_id: str, comment_id: str, updates: Dict[str, Any]):
    logger.info(f"Updating comment ID: {comment_id} for post ID: {post_id}")
    try:
        result = posts_collection.update_one(
            {"_id": ObjectId(post_id), "comments._id": ObjectId(comment_id)},
            {"$set": {"comments.$": updates}}
        )
        if result.modified_count > 0:
            logger.info(f"Successfully updated comment: {comment_id} for post: {post_id}")
        else:
            logger.warning(f"No changes made to comment: {comment_id} for post: {post_id}")
        return result
    except Exception as e:
        logger.error(f"Error updating comment {comment_id} for post {post_id}: {str(e)}")
        raise

def delete_comment(post_id: str, comment_id: str):
    logger.warning(f"Deleting comment ID: {comment_id} for post ID: {post_id}")
    try:
        result = posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$pull": {"comments": {"_id": ObjectId(comment_id)}}}
        )
        if result.modified_count > 0:
            logger.info(f"Successfully deleted comment: {comment_id} for post: {post_id}")
        else:
            logger.warning(f"Comment not found for deletion: {comment_id} for post: {post_id}")
        return result
    except Exception as e:
        logger.error(f"Error deleting comment {comment_id} for post {post_id}: {str(e)}")
        raise

def get_comments_by_user_id(user_id: str, limit: int = 100, skip: int = 0):
    logger.info(f"Retrieving comments by user ID: {user_id}")
    comments = []
    try:
        for post_data in posts_collection.find({"comments.user_id": user_id}).skip(skip).limit(limit).sort("created_at", -1):
            for comment in post_data.get("comments", []):
                if comment.get("user_id") == user_id:
                    comments.append(comment)
        logger.info(f"Retrieved {len(comments)} comments for user: {user_id}")
        return comments
    except Exception as e:
        logger.error(f"Error retrieving comments by user: {str(e)}")
        raise

# New Comment CRUD operations with separate collection
def create_comment_v2(comment: CommentModel):
    """Create a new comment in the separate comments collection."""
    comment_dict = comment.dict(by_alias=True, exclude_unset=True)
    if "_id" in comment_dict and comment_dict["_id"] is None:
        del comment_dict["_id"]
    
    logger.info(f"Creating new comment for post ID: {comment.post_id}")
    try:
        insert_result = comments_collection.insert_one(comment_dict)
        comment.id = str(insert_result.inserted_id)
        logger.info(f"Comment created with ID: {comment.id}")
        return comment
    except Exception as e:
        logger.error(f"Error creating comment: {str(e)}")
        raise

def get_comment_by_id(comment_id: str):
    """Retrieve a single comment by its ID."""
    logger.debug(f"Retrieving comment by ID: {comment_id}")
    try:
        comment_data = comments_collection.find_one({"_id": ObjectId(comment_id)})
        if comment_data:
            logger.debug(f"Found comment with ID: {comment_id}")
            return CommentModel(**comment_data)
        logger.debug(f"Comment not found with ID: {comment_id}")
        return None
    except Exception as e:
        logger.error(f"Error retrieving comment by ID: {str(e)}")
        raise

def update_comment_v2(comment_id: str, updates: Dict[str, Any]):
    """Update a comment with the specified fields."""
    logger.info(f"Updating comment with ID: {comment_id}")
    logger.debug(f"Update data: {updates}")
    try:
        result = comments_collection.update_one({"_id": ObjectId(comment_id)}, {"$set": updates})
        if result.modified_count > 0:
            logger.info(f"Successfully updated comment: {comment_id}")
        else:
            logger.warning(f"No changes made to comment: {comment_id}")
        return result
    except Exception as e:
        logger.error(f"Error updating comment {comment_id}: {str(e)}")
        raise

def delete_comment_v2(comment_id: str):
    """Delete a comment by its ID."""
    logger.warning(f"Deleting comment with ID: {comment_id}")
    try:
        result = comments_collection.delete_one({"_id": ObjectId(comment_id)})
        if result.deleted_count > 0:
            logger.info(f"Successfully deleted comment: {comment_id}")
        else:
            logger.warning(f"Comment not found for deletion: {comment_id}")
        return result
    except Exception as e:
        logger.error(f"Error deleting comment {comment_id}: {str(e)}")
        raise

def get_comments_for_post_v2(post_id: str, limit: int = 100, skip: int = 0):
    """Retrieve comments for a specific post with pagination."""
    logger.info(f"Retrieving comments for post ID: {post_id} with limit: {limit}, skip: {skip}")
    comments = []
    try:
        for comment_data in comments_collection.find({"post_id": post_id}).skip(skip).limit(limit).sort("created_at", -1):
            comments.append(CommentModel(**comment_data))
        logger.info(f"Retrieved {len(comments)} comments for post: {post_id}")
        return comments
    except Exception as e:
        logger.error(f"Error retrieving comments for post {post_id}: {str(e)}")
        raise

def get_comments_by_user_v2(user_id: str, limit: int = 100, skip: int = 0):
    """Retrieve comments by a specific user with pagination."""
    logger.info(f"Retrieving comments by user ID: {user_id} with limit: {limit}, skip: {skip}")
    comments = []
    try:
        for comment_data in comments_collection.find({"author_id": user_id}).skip(skip).limit(limit).sort("created_at", -1):
            comments.append(CommentModel(**comment_data))
        logger.info(f"Retrieved {len(comments)} comments for user: {user_id}")
        return comments
    except Exception as e:
        logger.error(f"Error retrieving comments by user {user_id}: {str(e)}")
        raise

def get_comment_replies(comment_id: str, limit: int = 100, skip: int = 0):
    """Retrieve replies to a specific comment with pagination."""
    logger.info(f"Retrieving replies for comment ID: {comment_id} with limit: {limit}, skip: {skip}")
    comments = []
    try:
        for comment_data in comments_collection.find({"parent_id": comment_id}).skip(skip).limit(limit).sort("created_at", -1):
            comments.append(CommentModel(**comment_data))
        logger.info(f"Retrieved {len(comments)} replies for comment: {comment_id}")
        return comments
    except Exception as e:
        logger.error(f"Error retrieving replies for comment {comment_id}: {str(e)}")
        raise

def setup_comment_indexes():
    """Set up MongoDB indexes for the comments collection for optimal performance."""
    logger.info("Setting up indexes for comments collection")
    try:
        # Create indexes for common query patterns
        comments_collection.create_index("post_id")
        comments_collection.create_index("author_id")
        comments_collection.create_index("parent_id")
        comments_collection.create_index("created_at")
        # Compound index for sorting comments by creation time within a post
        comments_collection.create_index([("post_id", 1), ("created_at", -1)])
        logger.info("Successfully created indexes for comments collection")
    except Exception as e:
        logger.error(f"Error setting up indexes for comments collection: {str(e)}")
        raise

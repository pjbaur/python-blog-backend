from fastapi.testclient import TestClient
from app.main import app
import pytest
from bson.objectid import ObjectId
from app.database import db
from app.tests.test_utils import create_test_token, mock_user, mock_user_with_tokens
from datetime import datetime, timezone
from jose import jwt
from app.auth import SECRET_KEY, ALGORITHM
from app.logger import get_logger

client = TestClient(app)
logger = get_logger(__name__)

# ********** Fixtures **********

@pytest.fixture
def create_test_post_with_comment(mock_user):
    """Fixture to create a test post with a comment for testing"""
    # Create a token for authentication
    token = create_test_token(data={"id": mock_user})
    
    # Add the token to the user's token list
    db['users'].update_one(
        {"_id": ObjectId(mock_user)},
        {"$push": {"tokens": token}}
    )
    
    # Create a test post
    test_post = {
        "title": "Test Post for Comments", 
        "content": "This is a post for testing comments",
        "categories": [],
        "is_published": True
    }
    
    response = client.post(
        "/api/v1/posts",
        headers={"Authorization": f"Bearer {token}"},
        json=test_post
    )
    
    post_data = response.json()
    logger.debug(f"post_data: {post_data}")
    post_id = post_data["id"]
    logger.debug(f"Post ID: {post_id}")
    
    # Create a test comment on the post
    test_comment = {
        "content": "This is a test comment"
    }
    
    comment_response = client.post(
        f"/api/v1/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json=test_comment
    )
    
    comment_data = comment_response.json()
    logger.debug(f"comment_data: {comment_data}")
    
    # Return post ID, comment ID, and token for use in tests
    yield {
        "post_id": post_id, 
        "comment_id": comment_data["id"], 
        "token": token, 
        "author_id": mock_user
    }
    
    # Clean up - remove the test post and comment
    db['posts'].delete_one({"_id": ObjectId(post_id)})
    db['comments'].delete_one({"_id": ObjectId(comment_data["id"])})

@pytest.fixture
def create_test_post_with_nested_comments(mock_user):
    """Fixture to create a test post with nested comments for testing"""
    # Create a token for authentication
    token = create_test_token(data={"id": mock_user})
    
    # Add the token to the user's token list
    db['users'].update_one(
        {"_id": ObjectId(mock_user)},
        {"$push": {"tokens": token}}
    )
    
    # Create a test post
    test_post = {
        "title": "Test Post for Nested Comments", 
        "content": "This is a post for testing nested comments",
        "categories": [],
        "is_published": True
    }
    
    response = client.post(
        "/api/v1/posts",
        headers={"Authorization": f"Bearer {token}"},
        json=test_post
    )
    
    post_data = response.json()
    post_id = post_data["id"]
    
    # Create a parent comment
    parent_comment = {
        "content": "This is a parent comment"
    }
    
    parent_response = client.post(
        f"/api/v1/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json=parent_comment
    )
    
    parent_data = parent_response.json()
    parent_id = parent_data["id"]
    
    # Create a child comment
    child_comment = {
        "content": "This is a child comment",
        "parent_id": parent_id
    }
    
    child_response = client.post(
        f"/api/v1/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json=child_comment
    )
    
    child_data = child_response.json()
    
    # Return post ID, parent comment ID, child comment ID, and token for use in tests
    yield {
        "post_id": post_id, 
        "parent_id": parent_id,
        "child_id": child_data["id"],
        "token": token, 
        "author_id": mock_user
    }
    
    # Clean up - remove the test post and comments
    db['posts'].delete_one({"_id": ObjectId(post_id)})
    db['comments'].delete_many({"post_id": post_id})

# ********** CRUD Tests **********

def test_create_comment_crud():
    """Test the CRUD create_comment_v2 function directly"""
    from app import crud
    from app.models import CommentModel
    
    # Create a test post first
    post_id = str(ObjectId())
    author_id = str(ObjectId())
    
    # Insert test post into database
    post_data = {
        "_id": ObjectId(post_id),
        "title": "Test Post for Comment CRUD",
        "content": "This is a post for testing comment CRUD",
        "author_id": author_id,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "categories": [],
        "is_published": True
    }
    
    db['posts'].insert_one(post_data)
    
    # Create test comment 
    comment = CommentModel(
        post_id=post_id,
        author_id=author_id,
        content="Test comment for CRUD testing",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_published=True
    )
    
    # Use CRUD function to create comment
    result = crud.create_comment_v2(comment)
    
    # Verify comment was added to the comments collection
    saved_comment = db['comments'].find_one({"post_id": post_id})
    assert saved_comment is not None
    assert saved_comment["content"] == comment.content
    assert saved_comment["author_id"] == author_id
    
    # Clean up
    db['posts'].delete_one({"_id": ObjectId(post_id)})
    db['comments'].delete_one({"_id": saved_comment["_id"]})

def test_get_comments_for_post_crud():
    """Test the CRUD get_comments_for_post_v2 function directly"""
    from app import crud
    from app.models import CommentModel
    
    # Create a test post
    post_id = str(ObjectId())
    author_id = str(ObjectId())
    
    # Insert test post into database
    post_data = {
        "_id": ObjectId(post_id),
        "title": "Test Post for Comment CRUD",
        "content": "This is a post for testing comment CRUD",
        "author_id": author_id,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "categories": [],
        "is_published": True
    }
    
    db['posts'].insert_one(post_data)
    
    # Create test comments directly in the comments collection
    comment1 = {
        "post_id": post_id,
        "author_id": author_id,
        "content": "Test comment 1",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "is_published": True
    }
    
    comment2 = {
        "post_id": post_id,
        "author_id": author_id,
        "content": "Test comment 2",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "is_published": True
    }
    
    comment1_id = db['comments'].insert_one(comment1).inserted_id
    comment2_id = db['comments'].insert_one(comment2).inserted_id
    
    # Use CRUD function to get comments
    comments = crud.get_comments_for_post_v2(post_id)
    
    # Verify comments were retrieved
    assert comments is not None
    assert len(comments) == 2
    comment_contents = [c.content for c in comments]
    assert "Test comment 1" in comment_contents
    assert "Test comment 2" in comment_contents
    
    # Clean up
    db['posts'].delete_one({"_id": ObjectId(post_id)})
    db['comments'].delete_many({"post_id": post_id})

def test_update_comment_crud():
    """Test the CRUD update_comment_v2 function directly"""
    from app import crud
    from app.models import CommentModel
    
    # Create a test post
    post_id = str(ObjectId())
    author_id = str(ObjectId())
    
    # Insert test post into database
    post_data = {
        "_id": ObjectId(post_id),
        "title": "Test Post for Comment CRUD",
        "content": "This is a post for testing comment CRUD",
        "author_id": author_id,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "categories": [],
        "is_published": True
    }
    
    db['posts'].insert_one(post_data)
    
    # Create test comment
    comment_data = {
        "post_id": post_id,
        "author_id": author_id,
        "content": "Original comment content",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "is_published": True
    }
    
    comment_id = db['comments'].insert_one(comment_data).inserted_id
    
    # Updated comment data
    updated_content = "Updated comment content"
    
    # Use CRUD function to update comment
    result = crud.update_comment_v2(str(comment_id), {"content": updated_content})
    
    # Verify comment was updated
    updated_comment = db['comments'].find_one({"_id": comment_id})
    assert updated_comment is not None
    assert updated_comment["content"] == updated_content
    
    # Clean up
    db['posts'].delete_one({"_id": ObjectId(post_id)})
    db['comments'].delete_one({"_id": comment_id})

def test_delete_comment_crud():
    """Test the CRUD delete_comment_v2 function directly"""
    from app import crud
    
    # Create a test post
    post_id = str(ObjectId())
    author_id = str(ObjectId())
    
    # Insert test post into database
    post_data = {
        "_id": ObjectId(post_id),
        "title": "Test Post for Comment CRUD",
        "content": "This is a post for testing comment CRUD",
        "author_id": author_id,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "categories": [],
        "is_published": True
    }
    
    db['posts'].insert_one(post_data)
    
    # Create test comment
    comment_data = {
        "post_id": post_id,
        "author_id": author_id,
        "content": "Comment to be deleted",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "is_published": True
    }
    
    comment_id = db['comments'].insert_one(comment_data).inserted_id
    
    # Use CRUD function to delete comment
    result = crud.delete_comment_v2(str(comment_id))
    
    # Verify comment was deleted
    deleted_comment = db['comments'].find_one({"_id": comment_id})
    assert deleted_comment is None
    
    # Clean up
    db['posts'].delete_one({"_id": ObjectId(post_id)})

# ********** API Endpoint Tests **********

def test_get_post_comments_api(create_test_post_with_comment):
    """Test the GET /{post_id}/comments endpoint"""
    post_id = create_test_post_with_comment["post_id"]
    token = create_test_post_with_comment["token"]
    
    response = client.get(
        f"/api/v1/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["post_id"] == post_id
    assert data[0]["content"] == "This is a test comment"
    assert "id" in data[0]
    assert "author_id" in data[0]
    assert "created_at" in data[0]

def test_create_post_comment_api(create_test_post_with_comment):
    """Test the POST /{post_id}/comments endpoint"""
    post_id = create_test_post_with_comment["post_id"]
    token = create_test_post_with_comment["token"]
    
    test_comment = {
        "content": "This is another test comment"
    }
    
    response = client.post(
        f"/api/v1/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json=test_comment
    )
    
    assert response.status_code == 201
    
    data = response.json()
    assert data["post_id"] == post_id
    assert data["content"] == test_comment["content"]
    assert "id" in data
    assert "author_id" in data
    assert "created_at" in data
    
    # Verify comment was added to the comments collection
    response = client.get(
        f"/api/v1/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    comments = response.json()
    assert len(comments) == 2
    
    # Clean up the new comment
    db['comments'].delete_one({"_id": ObjectId(data["id"])})

def test_create_nested_comment_api(create_test_post_with_comment):
    """Test creating a nested comment via the API"""
    post_id = create_test_post_with_comment["post_id"]
    parent_id = create_test_post_with_comment["comment_id"]
    token = create_test_post_with_comment["token"]
    
    # Create a child comment
    test_child_comment = {
        "content": "This is a reply to the original comment",
        "parent_id": parent_id
    }
    
    response = client.post(
        f"/api/v1/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json=test_child_comment
    )
    
    assert response.status_code == 201
    
    data = response.json()
    assert data["post_id"] == post_id
    assert data["content"] == test_child_comment["content"]
    assert data["parent_id"] == parent_id
    assert "id" in data
    assert "author_id" in data
    assert "created_at" in data
    
    # Clean up the child comment
    db['comments'].delete_one({"_id": ObjectId(data["id"])})

def test_get_nested_comments_api(create_test_post_with_nested_comments):
    """Test retrieving nested comments via the API"""
    post_id = create_test_post_with_nested_comments["post_id"]
    parent_id = create_test_post_with_nested_comments["parent_id"]
    child_id = create_test_post_with_nested_comments["child_id"]
    token = create_test_post_with_nested_comments["token"]
    
    response = client.get(
        f"/api/v1/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2  # Should have both parent and child comments
    
    # Find parent and child comments
    parent_comment = next((c for c in data if c["id"] == parent_id), None)
    child_comment = next((c for c in data if c["id"] == child_id), None)
    
    assert parent_comment is not None
    assert child_comment is not None
    
    # Verify parent-child relationship
    assert parent_comment["parent_id"] is None
    assert child_comment["parent_id"] == parent_id

def test_nonexistent_post_comments_api():
    """Test retrieving comments for a non-existent post"""
    # Generate a random ObjectId that doesn't exist
    non_existent_id = str(ObjectId())
    
    response = client.get(
        f"/api/v1/posts/{non_existent_id}/comments"
    )
    
    assert response.status_code == 404

def test_create_comment_nonexistent_post_api(mock_user):
    """Test creating a comment for a non-existent post"""
    # Create a token for authentication
    token = create_test_token(data={"id": mock_user})
    
    # Add the token to the user's token list
    db['users'].update_one(
        {"_id": ObjectId(mock_user)},
        {"$push": {"tokens": token}}
    )
    
    # Generate a random ObjectId that doesn't exist
    non_existent_id = str(ObjectId())
    
    test_comment = {
        "content": "This comment should not be created"
    }
    
    response = client.post(
        f"/api/v1/posts/{non_existent_id}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json=test_comment
    )
    
    assert response.status_code == 404

def test_create_comment_with_nonexistent_parent_api(create_test_post_with_comment):
    """Test creating a comment with a non-existent parent comment"""
    post_id = create_test_post_with_comment["post_id"]
    token = create_test_post_with_comment["token"]
    
    # Generate a random ObjectId that doesn't exist
    non_existent_parent_id = str(ObjectId())
    
    test_comment = {
        "content": "This comment should not be created",
        "parent_id": non_existent_parent_id
    }
    
    response = client.post(
        f"/api/v1/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json=test_comment
    )
    
    assert response.status_code == 404
    assert "Parent comment not found" in response.json()["detail"]

def test_unauthorized_comment_creation_api(create_test_post_with_comment):
    """Test that unauthorized users cannot create comments"""
    post_id = create_test_post_with_comment["post_id"]
    
    test_comment = {
        "content": "This comment should not be created without authorization"
    }
    
    # Attempt to create a comment without a token
    response = client.post(
        f"/api/v1/posts/{post_id}/comments",
        json=test_comment
    )
    
    assert response.status_code == 401
    
    # Attempt to create a comment with an invalid token
    invalid_token = "invalid.token.here"
    response = client.post(
        f"/api/v1/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {invalid_token}"},
        json=test_comment
    )
    
    assert response.status_code == 401
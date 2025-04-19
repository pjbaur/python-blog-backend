import pytest
from datetime import datetime
from bson.objectid import ObjectId
from unittest.mock import patch, MagicMock

from app.models import UserModel, PostModel
from app.crud import (
    # User operations
    create_user, get_user_by_email, get_user_by_id, get_all_users,
    update_user, delete_user,
    # Post operations
    create_post, get_post_by_id, get_all_posts, get_posts_by_author,
    update_post, delete_post, search_posts, filter_posts,
    get_filtered_posts, get_posts_by_category, get_posts_by_author_and_category
)

# ===== User CRUD Tests =====

@pytest.fixture
def mock_user_data():
    return {
        "_id": ObjectId("60d21b4667d0d8992e610c85"),
        "email": "test@example.com",
        "hashed_password": "hashed_password",
        "created_at": datetime.utcnow(),
        "is_active": True,
        "is_admin": False,
        "tokens": []
    }

@pytest.fixture
def mock_users_collection():
    with patch('app.crud.users_collection') as mock_collection:
        yield mock_collection

@pytest.fixture
def mock_posts_collection():
    with patch('app.crud.posts_collection') as mock_collection:
        yield mock_collection

class TestUserCRUD:
    
    def test_create_user(self, mock_users_collection, mock_user_data):
        # Setup
        user_model = UserModel(**mock_user_data)
        mock_users_collection.insert_one.return_value = MagicMock(
            inserted_id=mock_user_data["_id"]
        )
        
        # Execute
        result = create_user(user_model)
        
        # Verify
        mock_users_collection.insert_one.assert_called_once()
        assert result.id == str(mock_user_data["_id"])
        assert result.email == mock_user_data["email"]

    def test_create_user_without_id(self, mock_users_collection):
        # Setup
        user_data = {
            "email": "test@example.com",
            "hashed_password": "hashed_password",
            "is_active": True,
            "is_admin": False,
        }
        user_model = UserModel(**user_data)
        mock_users_collection.insert_one.return_value = MagicMock(
            inserted_id=ObjectId("60d21b4667d0d8992e610c85")
        )
        
        # Execute
        result = create_user(user_model)
        
        # Verify
        mock_users_collection.insert_one.assert_called_once()
        assert result.id == "60d21b4667d0d8992e610c85"
        assert result.email == user_data["email"]

    def test_create_user_exception(self, mock_users_collection, mock_user_data):
        # Setup
        user_model = UserModel(**mock_user_data)
        mock_users_collection.insert_one.side_effect = Exception("DB Error")
        
        # Execute & Verify
        with pytest.raises(Exception):
            create_user(user_model)

    def test_get_user_by_email(self, mock_users_collection, mock_user_data):
        # Setup
        mock_users_collection.find_one.return_value = mock_user_data
        
        # Execute
        result = get_user_by_email("test@example.com")
        
        # Verify
        mock_users_collection.find_one.assert_called_once_with({"email": "test@example.com"})
        assert result.id == str(mock_user_data["_id"])
        assert result.email == mock_user_data["email"]

    def test_get_user_by_email_not_found(self, mock_users_collection):
        # Setup
        mock_users_collection.find_one.return_value = None
        
        # Execute
        result = get_user_by_email("nonexistent@example.com")
        
        # Verify
        mock_users_collection.find_one.assert_called_once_with({"email": "nonexistent@example.com"})
        assert result is None

    def test_get_user_by_email_exception(self, mock_users_collection):
        # Setup
        mock_users_collection.find_one.side_effect = Exception("DB Error")
        
        # Execute & Verify
        with pytest.raises(Exception):
            get_user_by_email("test@example.com")

    def test_get_user_by_id(self, mock_users_collection, mock_user_data):
        # Setup
        user_id = str(mock_user_data["_id"])
        mock_users_collection.find_one.return_value = mock_user_data
        
        # Execute
        result = get_user_by_id(user_id)
        
        # Verify
        mock_users_collection.find_one.assert_called_once_with({"_id": ObjectId(user_id)})
        assert result.id == user_id
        assert result.email == mock_user_data["email"]

    def test_get_user_by_id_not_found(self, mock_users_collection):
        # Setup
        mock_users_collection.find_one.return_value = None
        
        # Execute
        result = get_user_by_id("60d21b4667d0d8992e610c85")
        
        # Verify
        assert result is None

    def test_get_all_users(self, mock_users_collection, mock_user_data):
        # Setup
        mock_users_collection.find.return_value = [mock_user_data, mock_user_data]
        
        # Execute
        result = get_all_users()
        
        # Verify
        mock_users_collection.find.assert_called_once()
        assert len(result) == 2
        assert result[0].id == str(mock_user_data["_id"])
        assert result[1].id == str(mock_user_data["_id"])

    def test_update_user(self, mock_users_collection, mock_user_data):
        # Setup
        user_id = str(mock_user_data["_id"])
        updates = {"is_active": False}
        mock_users_collection.update_one.return_value = MagicMock(modified_count=1)
        
        # Execute
        result = update_user(user_id, updates)
        
        # Verify
        mock_users_collection.update_one.assert_called_once_with(
            {"_id": ObjectId(user_id)}, {"$set": updates}
        )
        assert result.modified_count == 1

    def test_update_user_not_modified(self, mock_users_collection, mock_user_data):
        # Setup
        user_id = str(mock_user_data["_id"])
        updates = {"is_active": False}
        mock_users_collection.update_one.return_value = MagicMock(modified_count=0)
        
        # Execute
        result = update_user(user_id, updates)
        
        # Verify
        assert result.modified_count == 0

    def test_delete_user(self, mock_users_collection, mock_user_data):
        # Setup
        user_id = str(mock_user_data["_id"])
        mock_users_collection.delete_one.return_value = MagicMock(deleted_count=1)
        
        # Execute
        result = delete_user(user_id)
        
        # Verify
        mock_users_collection.delete_one.assert_called_once_with({"_id": ObjectId(user_id)})
        assert result.deleted_count == 1

    def test_delete_user_not_found(self, mock_users_collection):
        # Setup
        mock_users_collection.delete_one.return_value = MagicMock(deleted_count=0)
        
        # Execute
        result = delete_user("60d21b4667d0d8992e610c85")
        
        # Verify
        assert result.deleted_count == 0

# ===== Post CRUD Tests =====

@pytest.fixture
def mock_post_data():
    return {
        "_id": ObjectId("60d21b4667d0d8992e610c86"),
        "title": "Test Post",
        "content": "This is a test post content.",
        "author_id": "60d21b4667d0d8992e610c85",
        "created_at": datetime.utcnow()
    }

class TestPostCRUD:

    def test_create_post(self, mock_posts_collection, mock_post_data):
        # Setup
        post_model = PostModel(**mock_post_data)
        mock_posts_collection.insert_one.return_value = MagicMock(
            inserted_id=mock_post_data["_id"]
        )
        
        # Execute
        result = create_post(post_model)
        
        # Verify
        mock_posts_collection.insert_one.assert_called_once()
        assert result.id == str(mock_post_data["_id"])
        assert result.title == mock_post_data["title"]
        assert result.content == mock_post_data["content"]

    def test_get_post_by_id(self, mock_posts_collection, mock_post_data):
        # Setup
        post_id = str(mock_post_data["_id"])
        mock_posts_collection.find_one.return_value = mock_post_data
        
        # Execute
        result = get_post_by_id(post_id)
        
        # Verify
        mock_posts_collection.find_one.assert_called_once_with({"_id": ObjectId(post_id)})
        assert result.id == post_id
        assert result.title == mock_post_data["title"]
        assert result.content == mock_post_data["content"]

    def test_get_post_by_id_not_found(self, mock_posts_collection):
        # Setup
        mock_posts_collection.find_one.return_value = None
        
        # Execute
        result = get_post_by_id("60d21b4667d0d8992e610c86")
        
        # Verify
        assert result is None

    def test_get_all_posts(self, mock_posts_collection, mock_post_data):
        # Setup
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.sort.return_value = [mock_post_data, mock_post_data]
        mock_posts_collection.find.return_value = mock_cursor
        
        # Execute
        result = get_all_posts(limit=10, skip=0)
        
        # Verify
        mock_posts_collection.find.assert_called_once()
        mock_cursor.skip.assert_called_once_with(0)
        mock_cursor.limit.assert_called_once_with(10)
        mock_cursor.sort.assert_called_once_with("created_at", -1)
        assert len(result) == 2

    def test_get_posts_by_author(self, mock_posts_collection, mock_post_data):
        # Setup
        author_id = "60d21b4667d0d8992e610c85"
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.sort.return_value = [mock_post_data]
        mock_posts_collection.find.return_value = mock_cursor
        
        # Execute
        result = get_posts_by_author(author_id, limit=10, skip=0)
        
        # Verify
        mock_posts_collection.find.assert_called_once_with({"author_id": author_id})
        mock_cursor.skip.assert_called_once_with(0)
        mock_cursor.limit.assert_called_once_with(10)
        mock_cursor.sort.assert_called_once_with("created_at", -1)
        assert len(result) == 1
        assert result[0].author_id == author_id

    def test_update_post(self, mock_posts_collection, mock_post_data):
        # Setup
        post_id = str(mock_post_data["_id"])
        updates = {"title": "Updated Title"}
        mock_posts_collection.update_one.return_value = MagicMock(modified_count=1)
        
        # Execute
        result = update_post(post_id, updates)
        
        # Verify
        mock_posts_collection.update_one.assert_called_once_with(
            {"_id": ObjectId(post_id)}, {"$set": updates}
        )
        assert result.modified_count == 1

    def test_delete_post(self, mock_posts_collection, mock_post_data):
        # Setup
        post_id = str(mock_post_data["_id"])
        mock_posts_collection.delete_one.return_value = MagicMock(deleted_count=1)
        
        # Execute
        result = delete_post(post_id)
        
        # Verify
        mock_posts_collection.delete_one.assert_called_once_with({"_id": ObjectId(post_id)})
        assert result.deleted_count == 1

    def test_search_posts(self, mock_posts_collection, mock_post_data):
        # Setup
        query = "test"
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.sort.return_value = [mock_post_data]
        mock_posts_collection.find.return_value = mock_cursor
        
        # Execute
        result = search_posts(query, limit=10, skip=0)
        
        # Verify
        mock_posts_collection.find.assert_called_once_with({"$text": {"$search": query}})
        mock_cursor.skip.assert_called_once_with(0)
        mock_cursor.limit.assert_called_once_with(10)
        mock_cursor.sort.assert_called_once_with("created_at", -1)
        assert len(result) == 1

    def test_filter_posts(self, mock_posts_collection, mock_post_data):
        # Setup
        filters = {"author_id": "60d21b4667d0d8992e610c85"}
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.sort.return_value = [mock_post_data]
        mock_posts_collection.find.return_value = mock_cursor
        
        # Execute
        result = filter_posts(filters, limit=10, skip=0)
        
        # Verify
        mock_posts_collection.find.assert_called_once_with(filters)
        mock_cursor.skip.assert_called_once_with(0)
        mock_cursor.limit.assert_called_once_with(10)
        mock_cursor.sort.assert_called_once_with("created_at", -1)
        assert len(result) == 1

    def test_get_filtered_posts(self, mock_posts_collection, mock_post_data):
        # Setup
        filters = {"author_id": "60d21b4667d0d8992e610c85"}
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.sort.return_value = [mock_post_data]
        mock_posts_collection.find.return_value = mock_cursor
        
        # Execute
        result = get_filtered_posts(skip=0, limit=10, filters=filters, sort_by="title", sort_direction=1)
        
        # Verify
        mock_posts_collection.find.assert_called_once_with(filters)
        mock_cursor.skip.assert_called_once_with(0)
        mock_cursor.limit.assert_called_once_with(10)
        mock_cursor.sort.assert_called_once_with("title", 1)
        assert len(result) == 1

    def test_get_posts_by_category(self, mock_posts_collection, mock_post_data):
        # Setup
        category_id = 1
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.sort.return_value = [mock_post_data]
        mock_posts_collection.find.return_value = mock_cursor
        
        # Execute
        result = get_posts_by_category(category_id, limit=10, skip=0)
        
        # Verify
        mock_posts_collection.find.assert_called_once_with({"category_id": category_id})
        mock_cursor.skip.assert_called_once_with(0)
        mock_cursor.limit.assert_called_once_with(10)
        mock_cursor.sort.assert_called_once_with("created_at", -1)
        assert len(result) == 1

    def test_get_posts_by_author_and_category(self, mock_posts_collection, mock_post_data):
        # Setup
        author_id = "60d21b4667d0d8992e610c85"
        category_id = 1
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.sort.return_value = [mock_post_data]
        mock_posts_collection.find.return_value = mock_cursor
        
        # Execute
        result = get_posts_by_author_and_category(author_id, category_id, limit=10, skip=0)
        
        # Verify
        mock_posts_collection.find.assert_called_once_with({"author_id": author_id, "category_id": category_id})
        mock_cursor.skip.assert_called_once_with(0)
        mock_cursor.limit.assert_called_once_with(10)
        mock_cursor.sort.assert_called_once_with("created_at", -1)
        assert len(result) == 1
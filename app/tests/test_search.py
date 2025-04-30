import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import json

from ..main import app
from .. import crud, schemas
from ..routers.search import SearchType

client = TestClient(app)

# Define test data
mock_post_id = str(ObjectId())
mock_post_id2 = str(ObjectId())
mock_user_id = str(ObjectId())
mock_comment_id = str(ObjectId())
created_time = datetime.utcnow()
updated_time = created_time + timedelta(hours=1)

# Mock post data
mock_post = {
    "_id": ObjectId(mock_post_id),
    "title": "Test Post Title",
    "content": "This is a test post content with searchable keywords",
    "author_id": mock_user_id,
    "created_at": created_time,
    "updated_at": updated_time,
    "is_published": True
}

mock_post2 = {
    "_id": ObjectId(mock_post_id2),
    "title": "Another Test Post",
    "content": "Different content with some search terms",
    "author_id": mock_user_id,
    "created_at": created_time - timedelta(days=1),
    "updated_at": updated_time - timedelta(days=1),
    "is_published": True
}

# Mock comment data
mock_comment = {
    "_id": ObjectId(mock_comment_id),
    "post_id": mock_post_id,
    "author_id": mock_user_id,
    "content": "This is a test comment with searchable keywords",
    "created_at": created_time,
    "updated_at": updated_time,
    "is_published": True,
    "parent_id": None
}

# Helper function to create proper model objects
def create_post_model(post_dict):
    """Convert dictionary to PostModel with content_preview added"""
    post = crud.PostModel(**post_dict)
    post.content_preview = post.content[:200] + "..." if len(post.content) > 200 else post.content
    return post

def create_comment_model(comment_dict):
    """Convert dictionary to CommentModel with content_preview added"""
    comment = crud.CommentModel(**comment_dict)
    comment.content_preview = comment.content[:200] + "..." if len(comment.content) > 200 else comment.content
    return comment


class TestSearchEndpoints:
    """Test cases for the search API endpoints"""

    @patch('app.crud.search_posts_v2')
    @patch('app.crud.search_comments')
    def test_search_all(self, mock_search_comments, mock_search_posts_v2):
        """Test searching for both posts and comments"""
        # Setup mock returns
        mock_search_posts_v2.return_value = [create_post_model(mock_post)]
        mock_search_comments.return_value = [create_comment_model(mock_comment)]
        
        # Execute the request
        response = client.get("/api/v1/search?q=test+searchable")
        
        print(f">>>>>Response.json(): {response.json()}")

        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["page"] == 0
        assert data["limit"] == 10
        assert len(data["results"]) == 2
        
        # Verify the posts in the results
        posts = [r for r in data["results"] if r["type"] == "post"]
        assert len(posts) == 1
        assert "This is a test post content" in posts[0]["content_preview"]
        
        # Verify the comments in the results
        comments = [r for r in data["results"] if r["type"] == "comment"]
        assert len(comments) == 1
        assert "test comment" in comments[0]["content_preview"]
        
        # Verify the mocks were called correctly
        mock_search_posts_v2.assert_called_once_with(
            query="test searchable", 
            limit=5,  # limit // 2 for 'all' type
            skip=0, 
            sort_by="relevance", 
            sort_direction=-1
        )
        mock_search_comments.assert_called_once_with(
            query="test searchable", 
            limit=5,  # limit // 2 for 'all' type
            skip=0, 
            sort_by="relevance", 
            sort_direction=-1
        )

    @patch('app.crud.search_posts_v2')
    def test_search_posts_only(self, mock_search_posts_v2):
        """Test searching for only posts"""
        # Setup mock returns
        mock_search_posts_v2.return_value = [create_post_model(mock_post), create_post_model(mock_post2)]
        
        # Execute the request
        response = client.get("/api/v1/search?q=test&type=posts")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["results"]) == 2
        
        # All results should be posts
        for result in data["results"]:
            assert result["type"] == "post"
        
        # Verify the mocks were called correctly
        mock_search_posts_v2.assert_called_once_with(
            query="test", 
            limit=10,  # full limit for 'posts' type
            skip=0, 
            sort_by="relevance", 
            sort_direction=-1
        )

    @patch('app.crud.search_comments')
    def test_search_comments_only(self, mock_search_comments):
        """Test searching for only comments"""
        # Setup mock returns
        mock_search_comments.return_value = [create_comment_model(mock_comment)]
        
        # Execute the request
        response = client.get("/api/v1/search?q=test+comment&type=comments")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["results"]) == 1
        
        # All results should be comments
        for result in data["results"]:
            assert result["type"] == "comment"
        
        # Verify the mocks were called correctly
        mock_search_comments.assert_called_once_with(
            query="test comment", 
            limit=10,  # full limit for 'comments' type
            skip=0, 
            sort_by="relevance", 
            sort_direction=-1
        )

    @patch('app.crud.search_posts_v2')
    @patch('app.crud.search_comments')
    def test_search_with_pagination(self, mock_search_comments, mock_search_posts_v2):
        """Test search with pagination parameters"""
        # Setup mock returns
        mock_search_posts_v2.return_value = [create_post_model(mock_post)]
        mock_search_comments.return_value = []
        
        # Execute the request with pagination
        response = client.get("/api/v1/search?q=test&page=1&limit=5")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 5
        
        # Verify the mocks were called correctly with pagination parameters
        mock_search_posts_v2.assert_called_once_with(
            query="test", 
            limit=2,  # limit // 2 for 'all' type with limit=5
            skip=0,  # For 'all' type, skip is 0 in the split search 
            sort_by="relevance", 
            sort_direction=-1
        )

    @patch('app.crud.search_posts_v2')
    @patch('app.crud.search_comments')
    def test_search_with_created_at_sorting(self, mock_search_comments, mock_search_posts_v2):
        """Test search with created_at sorting"""
        # Setup mock returns with multiple posts to test sorting
        mock_posts = [create_post_model(mock_post), create_post_model(mock_post2)]
        mock_search_posts_v2.return_value = mock_posts
        mock_search_comments.return_value = []
        
        # Execute the request with created_at sorting
        response = client.get("/api/v1/search?q=test&sort_by=created_at")
        
        # Verify the response
        assert response.status_code == 200
        
        # Verify the mocks were called correctly with sort parameters
        mock_search_posts_v2.assert_called_once_with(
            query="test", 
            limit=5,
            skip=0, 
            sort_by="created_at",  # Sorting by created_at
            sort_direction=-1
        )

    @patch('app.crud.search_posts_v2')
    def test_search_with_invalid_sort_parameter(self, mock_search_posts_v2):
        """Test search with invalid sort parameter falls back to default"""
        # Setup mock return
        mock_search_posts_v2.return_value = [create_post_model(mock_post)]
        
        # Execute request with invalid sort_by parameter
        response = client.get("/api/v1/search?q=test&type=posts&sort_by=invalid_field")
        
        # Verify the response
        assert response.status_code == 200
        
        # Verify it fell back to the default "relevance" sort
        mock_search_posts_v2.assert_called_once_with(
            query="test", 
            limit=10,
            skip=0, 
            sort_by="relevance",  # Should fall back to relevance
            sort_direction=-1
        )

    @patch('app.crud.search_posts_v2')
    def test_empty_search_results(self, mock_search_posts_v2):
        """Test search with no matching results"""
        # Setup mock to return empty list
        mock_search_posts_v2.return_value = []
        
        # Execute request
        response = client.get("/api/v1/search?q=nonexistentterm&type=posts")
        
        # Verify empty results
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["results"]) == 0

    @patch('app.crud.search_posts_v2')
    def test_search_error_handling(self, mock_search_posts_v2):
        """Test search error handling"""
        # Setup mock to raise an exception
        mock_search_posts_v2.side_effect = Exception("Database error")
        
        # Execute request
        response = client.get("/api/v1/search?q=test&type=posts")
        
        # Verify error response
        assert response.status_code == 500
        assert response.json()["detail"] == "Error performing search on posts"


class TestSearchCrudFunctions:
    """Test cases for the search CRUD functions"""
    
    @patch('app.crud.posts_collection.find')
    def test_search_posts_v2(self, mock_find):
        """Test the search_posts_v2 CRUD function"""
        # Setup mock cursor
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = [mock_post, mock_post2]
        
        mock_find.return_value = mock_cursor
        
        # Call the function
        results = crud.search_posts_v2(query="test", limit=10, skip=0, sort_by="relevance")
        
        # Verify the results
        assert len(results) == 2
        assert results[0].id == mock_post_id
        assert results[1].id == mock_post_id2
        
        # Verify MongoDB query was correct
        mock_find.assert_called_once_with(
            {"$text": {"$search": "test"}, "is_published": True},
            projection={"score": {"$meta": "textScore"}}
        )
        
        # Verify sorting, skip, and limit
        mock_cursor.sort.assert_called_once_with({"score": {"$meta": "textScore"}})
        mock_cursor.skip.assert_called_once_with(0)
        mock_cursor.limit.assert_called_once_with(10)

    @patch('app.crud.comments_collection.find')
    def test_search_comments(self, mock_find):
        """Test the search_comments CRUD function"""
        # Setup mock cursor
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = [mock_comment]
        
        mock_find.return_value = mock_cursor
        
        # Call the function
        results = crud.search_comments(query="test comment", limit=10, skip=0, sort_by="created_at", sort_direction=-1)
        
        # Verify the results
        assert len(results) == 1
        assert results[0].id == mock_comment_id
        
        # Verify MongoDB query was correct
        mock_find.assert_called_once_with(
            {"$text": {"$search": "test comment"}, "is_published": True},
            projection={"score": {"$meta": "textScore"}}
        )
        
        # Verify sorting, skip, and limit
        mock_cursor.sort.assert_called_once_with({"created_at": -1})
        mock_cursor.skip.assert_called_once_with(0)
        mock_cursor.limit.assert_called_once_with(10)

    @patch('app.crud.posts_collection.create_index')
    @patch('app.crud.comments_collection.create_index')
    def test_setup_search_indexes(self, mock_comments_create_index, mock_posts_create_index):
        """Test the setup_search_indexes function"""
        # Call the function
        crud.setup_search_indexes()
        
        # Verify indexes were created correctly
        mock_posts_create_index.assert_called_once_with([
            ("title", "text"), 
            ("content", "text")
        ], name="post_text_search")
        
        mock_comments_create_index.assert_called_once_with([
            ("content", "text")
        ], name="comment_text_search")
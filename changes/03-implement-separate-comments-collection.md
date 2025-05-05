I'll help you plan a thorough implementation to move comments to their own collection. Let me map out a detailed approach for this change.

# Implementation Plan: Separate Collection for Comments

## 1. Current Implementation Analysis

Currently, comments are stored inside the post documents as an embedded array. This approach has advantages for simple retrieval but presents scaling limitations:

- Comments grow with posts, potentially hitting MongoDB document size limits (16MB)
- Querying and updating individual comments requires accessing the entire post
- Inefficient if you need to filter/sort comments independently from posts

## 2. Proposed Architecture

We'll create a dedicated `comments_collection` in MongoDB with these key characteristics:

- Each comment will be a separate document with its own ObjectId
- Comments will reference posts through a `post_id` field
- User identification will be maintained through `user_id` field
- Comments can be indexed, queried, and managed independently

## 3. Implementation Tasks

### 3.1. Schema and Model Updates
- Create a `CommentModel` in `models.py`
- Update `schemas.py` to include comment request/response schemas
- Ensure proper reference fields in both models (post_id, user_id)

### 3.2. Database Layer Updates
- Add `comments_collection = db['comments']` in `crud.py`
- Implement full CRUD operations for the new collection
- Maintain proper references between posts and comments

### 3.3. API and Routing Updates
- Update or create comment-related API endpoints in `routers/comments.py`
- Ensure proper authentication and authorization checks
- Implement appropriate response formats

### 3.4. Migration Strategy
- Create a data migration script to move existing comments
- Maintain comment metadata (timestamps, user info)
- Handle the transition period where both systems might coexist

### 3.5. Testing
- Update existing tests to accommodate the new structure
- Add new tests for comment-specific functionality
- Test performance with high comment volumes

## 4. Detailed Technical Specifications

### 4.1. Comment Model Structure
```python
class CommentModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    post_id: str
    user_id: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_deleted: bool = False
    parent_id: Optional[str] = None  # For nested comments/replies
```

### 4.2. CRUD Operations
New functions needed:
- `create_comment(comment: CommentModel)`
- `get_comment_by_id(comment_id: str)`
- `update_comment(comment_id: str, updates: Dict[str, Any])`
- `delete_comment(comment_id: str)`
- `get_comments_for_post(post_id: str, limit: int, skip: int)`
- `get_comments_by_user(user_id: str, limit: int, skip: int)`
- `get_comment_replies(comment_id: str)`

### 4.3. API Endpoints
- `POST /posts/{post_id}/comments` - Create comment
- `GET /posts/{post_id}/comments` - List comments for post
- `GET /comments/{comment_id}` - Get single comment
- `PUT /comments/{comment_id}` - Update comment
- `DELETE /comments/{comment_id}` - Delete comment
- `GET /users/{user_id}/comments` - Get user's comments
- `POST /comments/{comment_id}/replies` - Add reply to comment

### 4.4. Indexes for Performance
MongoDB indexes needed:
- `post_id` - For fast retrieval of comments by post
- `user_id` - For fast retrieval of user's comments
- `parent_id` - For finding replies to comments
- `created_at` - For sorting by time
- Compound index `(post_id, created_at)` - For sorting post comments chronologically

## 5. Benefits of the New Approach

1. **Scalability**: No document size limits for comments on popular posts
2. **Performance**: Faster operations on individual comments
3. **Flexibility**: Independent querying and sorting of comments
4. **Feature extensibility**: Easier to add features like:
   - Comment threading/nesting
   - Comment moderation queue
   - Comment reactions/voting
   - Comment search

## 6. Potential Challenges

1. **Data consistency**: Ensuring referential integrity between posts and comments
2. **Migration complexity**: Moving existing embedded comments to new collection
3. **Transactional operations**: MongoDB's limited transaction support
4. **Query complexity**: Some operations may require multiple queries or aggregation
5. **Performance tradeoffs**: Some post+comments views may require joining data

## Next Steps

If you'd like me to proceed with implementation, I can:
1. Create the CommentModel in models.py
2. Update the comment CRUD operations in crud.py
3. Create/modify endpoints in routers/comments.py
4. Create a migration script for existing data
5. Update tests

Would you like me to start implementing this plan? Which part would you like me to tackle first?
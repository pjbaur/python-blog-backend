# REST API Endpoints Design

## Authentication Requirements Legend
- **🌎 Public** - No authentication required
- **🔑 Authenticated** - Valid JWT token required
- **👑 Admin** - Admin privileges required

## Authentication Endpoints

### `POST /api/v1/auth/register` 🌎
- Creates a new user account
- **Request Body**: `{ "email": string, "password": string }`
- **Response**: `{ "id": int, "email": string, "role": string }`

### `POST /api/v1/auth/login` 🌎
- Authenticates a user and returns JWT tokens
- **Request Body**: `{ "email": string, "password": string }`
- **Response**: `{ "access_token": string, "refresh_token": string, "token_type": "bearer" }`

### `POST /api/v1/auth/refresh` 🌎
- Refreshes an expired access token
- **Request Body**: `{ "refresh_token": string }`
- **Response**: `{ "access_token": string, "token_type": "bearer" }`

### `POST /api/v1/auth/logout` 🔑
- Invalidates current tokens
- **Request Body**: `{ "refresh_token": string }`
- **Response**: `{ "detail": "Successfully logged out" }`

### `POST /api/v1/auth/change-password` 🔑
- Updates current user's password in the database and returns new tokens
- **Request Body**: `{ "current_password": string, "new_password": string, "confirm_password": string}`
- **Response**: `{ "access_token": string, "refresh_token": string, "token_type": "bearer" }`

## User Endpoints

### `GET /api/v1/users/me` 🔑
- Returns the current authenticated user's profile
- **Response**: `{ "id": int, "email": string, "role": string, "created_at": datetime }`

### `GET /api/v1/users/{user_id}` 🌎
- Returns a specific user's public profile
- **Response**: `{ "id": int, "email": string, "role": string, "created_at": datetime }`

### `PUT /api/v1/users/me` 🔑
- Updates the current user's profile
- **Request Body**: `{ "email": string, "password": string }`
- **Response**: `{ "id": int, "email": string, "role": string }`

### `GET /api/v1/users/{user_id}/posts` 🌎
- Returns all posts by a specific user
- **Query Parameters**: `page`, `limit`, `sort_by`, `order`
- **Response**: Array of post objects with pagination metadata

## Post Endpoints

### `GET /api/v1/posts` 🌎
- Returns a list of published posts
- **Query Parameters**: `page`, `limit`, `sort_by`, `order`, `category`, `hashtag`
- **Response**: Array of post objects with pagination metadata

### `GET /api/v1/posts/{post_id}` 🌎
- Returns a specific post with its details
- **Response**: Complete post object including author details

### `POST /api/v1/posts` 🔑
- Creates a new post
- **Request Body**: `{ "title": string, "content": string, "categories": [int], "is_published": boolean }`
- **Response**: Created post object

### `PUT /api/v1/posts/{post_id}` 🔑
- Updates an existing post (requires ownership of the post)
- **Request Body**: `{ "title": string, "content": string, "categories": [int], "is_published": boolean }`
- **Response**: Updated post object

### `DELETE /api/v1/posts/{post_id}` 🔑
- Deletes a post (requires ownership of the post or admin role)
- **Response**: `{ "detail": "Post successfully deleted" }`

### `POST /api/v1/posts/{post_id}/images` 🔑
- Uploads an image for a post (requires ownership of the post)
- **Request Body**: Multipart form data with image file
- **Response**: `{ "id": int, "filename": string, "url": string }`

## Comment Endpoints

### `GET /api/v1/posts/{post_id}/comments` 🌎
- Returns all comments for a specific post
- **Query Parameters**: `page`, `limit`
- **Response**: Array of comment objects with threaded structure

### `POST /api/v1/posts/{post_id}/comments` 🔑
- Creates a new comment on a post
- **Request Body**: `{ "body": string, "parent_id": int (optional) }`
- **Response**: Created comment object

### `PUT /api/v1/comments/{comment_id}` 🔑
- Updates an existing comment (requires ownership of the comment)
- **Request Body**: `{ "body": string }`
- **Response**: Updated comment object

### `DELETE /api/v1/comments/{comment_id}` 🔑
- Deletes a comment (requires ownership of the comment or admin role)
- **Response**: `{ "detail": "Comment successfully deleted" }`

### `POST /api/v1/comments/{comment_id}/replies` 🔑
- Creates a reply to a comment
- **Request Body**: `{ "body": string }`
- **Response**: Created comment object

## Admin Endpoints

### `GET /api/v1/admin/users` 👑
- Lists all users (requires admin role)
- **Response**: Array of User objects

## Category Endpoints

### `GET /api/v1/categories` 🌎
- Returns all available categories
- **Response**: Array of category objects

### `POST /api/v1/categories` 👑
- Creates a new category (requires admin role)
- **Request Body**: `{ "name": string, "description": string }`
- **Response**: Created category object

### `PUT /api/v1/categories/{category_id}` 👑
- Updates a category (requires admin role)
- **Request Body**: `{ "name": string, "description": string }`
- **Response**: Updated category object

### `DELETE /api/v1/categories/{category_id}` 👑
- Deletes a category (requires admin role)
- **Response**: `{ "detail": "Category successfully deleted" }`

## Search Endpoint

### `GET /api/v1/search` 🌎
- Performs a full-text search across posts and comments
- **Query Parameters**: `q` (search term), `page`, `limit`, `type` (posts/comments/all)
- **Response**: Array of matching objects with pagination metadata

## Hashtag Endpoints

### `GET /api/v1/hashtags` 🌎
- Returns all available hashtags
- **Query Parameters**: `page`, `limit`
- **Response**: Array of hashtag objects

### `GET /api/v1/hashtags/{hashtag_name}/posts` 🌎
- Returns all posts with a specific hashtag
- **Query Parameters**: `page`, `limit`
- **Response**: Array of post objects with pagination metadata

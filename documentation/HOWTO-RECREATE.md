pjbaur: Don't make any changes. Please describe this application exaustively so that it could be duplicated by supplying your answer to an AI prompt. Include its features, user workflows, and data requirements.

GitHub Copilot: # Python Blog Backend Application Overview

I'll provide an exhaustive description of the Python blog backend application based on the codebase, covering its architecture, features, user workflows, and data requirements.

## 1. General Overview

This is a feature-rich RESTful API backend for a blog platform built with Python, FastAPI, and MongoDB. It follows modern development practices with JWT authentication, proper password hashing, and a structured modular design.

## 2. Technical Stack

- **Framework**: FastAPI
- **Database**: MongoDB
- **Authentication**: JWT (JSON Web Tokens) with access and refresh tokens
- **Password Security**: Bcrypt hashing via passlib
- **Logging**: Custom logging implementation
- **Containerization**: Docker support

## 3. Core Architecture

The application follows a clean, modular architecture:

- **Routes**: Central routing through routes.py
- **Routers**: Modular endpoints organized by domain in app/routers/
- **Models**: Pydantic models for data validation in models.py
- **Schemas**: Request/response schemas in schemas.py
- **CRUD Operations**: Database operations in crud.py
- **Authentication**: JWT implementation in auth.py
- **Database**: MongoDB connection in database.py
- **Logging**: Custom logger in logger.py

## 4. Data Models

### 4.1 User
- Email (unique identifier)
- Hashed password
- Active status
- Admin status
- Created/updated timestamps
- Tokens list

### 4.2 Post
- Title
- Content
- Author ID
- Created/updated timestamps
- Categories
- Publication status

### 4.3 Comment
- Content
- Post ID
- Author ID
- Parent ID (for nested comments)
- Created/updated timestamps
- Publication status

### 4.4 Token Information
- Token string
- Expiration timestamp

## 5. Feature Set

### 5.1 Authentication
- User registration
- User login with JWT (access and refresh tokens)
- Token refresh functionality
- Logout with token invalidation
- Password hashing and verification

### 5.2 User Management
- User profile retrieval
- User profile updates
- User listing (admin only)
- Automatic admin user creation

### 5.3 Blog Post Management
- Create posts
- Read posts (single or paginated lists)
- Update posts
- Delete posts
- Filter posts by author
- Sort posts by different criteria

### 5.4 Comment System
- Add comments to posts
- Nested comments (replies)
- Edit comments
- Delete comments

### 5.5 Admin Functionality
- User management
- Content moderation capabilities

### 5.6 Image Uploads
- Support for image uploads
- Image storage in uploads/images directory

## 6. API Endpoints

### 6.1 Authentication Endpoints
- POST /auth/register - Register new user
- POST /auth/login - Authenticate and get tokens
- POST /auth/refresh - Refresh access token
- POST /auth/logout - Invalidate tokens

### 6.2 User Endpoints
- GET /users/me - Get current user profile
- PUT /users/me - Update current user profile
- GET /users/{user_id} - Get user by ID
- GET /users/{user_id}/posts - Get posts by user

### 6.3 Post Endpoints
- POST /posts - Create new post
- GET /posts - Get all posts with pagination
- GET /posts/{post_id} - Get post by ID
- PUT /posts/{post_id} - Update post
- DELETE /posts/{post_id} - Delete post

### 6.4 Comment Endpoints
- POST /posts/{post_id}/comments - Add comment to post
- GET /posts/{post_id}/comments - Get comments for post
- PUT /comments/{comment_id} - Update comment
- DELETE /comments/{comment_id} - Delete comment

### 6.5 Admin Endpoints
- GET /admin/users - Get all users (admin only)

## 7. User Workflows

### 7.1 User Registration and Authentication
1. User registers with email and password
2. System validates inputs and creates user
3. User logs in with credentials
4. System provides access and refresh tokens
5. User includes access token in subsequent requests
6. When access token expires, user refreshes with refresh token
7. On logout, both tokens are invalidated

### 7.2 Content Creation Workflow
1. Authenticated user creates a blog post
2. System stores post and associates it with user
3. Post appears in the global feed and user's personal feed
4. Other users can view the post
5. Author can edit or delete their posts

### 7.3 Commenting Workflow
1. User views a post
2. User adds a comment to the post
3. Comment appears with the post
4. Users can reply to existing comments
5. Comment authors can edit or delete their comments

### 7.4 User Profile Management
1. User retrieves their profile information
2. User updates profile details
3. System validates and saves changes

### 7.5 Admin Workflow
1. Admin user logs in
2. Admin accesses special admin endpoints
3. Admin can view all users and manage system

## 8. Data Requirements

### 8.1 Database Structure
- Users collection for user data
- Posts collection for blog posts
- Comments collection (based on code references, though may use post references)

### 8.2 Environment Configuration
- MongoDB connection string
- JWT secret key
- Token expiration settings
- Initial admin credentials
- Logging configuration

### 8.3 File Storage
- Uploaded images stored in filesystem
- Organized directory structure for uploads

## 9. Security Measures

- Password hashing with bcrypt
- JWT with short-lived access tokens
- Refresh token mechanism for extended sessions
- Token invalidation on logout
- Role-based access control
- Input validation with Pydantic

## 10. Testing

Comprehensive test suite covering:
- Authentication functionality
- CRUD operations
- Admin capabilities
- User management
- Post and comment features
- Token handling and expiration

## 11. Deployment

- Docker containerization support
- Environment variable configuration
- Logging for production monitoring

## 12. Planned Features

Based on the changes directory, these features are likely in development:
- Password change functionality
- Enhanced comment system implementation

This application provides a robust foundation for a blog platform with comprehensive user management, content creation, and social interaction capabilities. The separation of concerns in the architecture would make it maintainable and extensible for future features.
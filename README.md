# Python Blog Backend API

A RESTful API backend for a blog application built with FastAPI and MongoDB.

## Features

- **User Authentication**: JWT-based authentication with secure password hashing
- **User Management**: Registration, login, and user profile endpoints
- **Blog Post Management**: Create, read, update, and delete blog posts
- **Comment System**: Support for nested comments on blog posts
- **Admin Panel**: Protected endpoints for administrative functions
- **Dockerized**: Easy deployment with Docker

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [MongoDB](https://www.mongodb.com/)
- **Authentication**: JWT tokens via [python-jose](https://github.com/mpdavis/python-jose) and [passlib](https://passlib.readthedocs.io/)
- **Testing**: [pytest](https://docs.pytest.org/)
- **Containerization**: Docker

## Prerequisites

- Python 3.10+
- MongoDB
- Docker (optional)

## Installation

### Local Setup

1. Clone the repository:
   ```
   git clone https://github.com/pjbaur/python-blog-backend.git
   cd python-blog-backend
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following variables (copy the file env.template):
   ```
   MONGO_URI=mongodb://localhost:27017/
   SECRET_KEY=your_jwt_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. Start the application:
   ```
   uvicorn app.main:app --reload
   ```

### Docker Setup

1. Build and run the Docker container:
   ```
   docker build -t blog-backend .
   docker run -p 8000:8000 --env-file .env blog-backend
   ```

## API Endpoints

### Healthcheck
- GET /api/v1/healthcheck — Healthcheck endpoint

### Authentication
- POST /api/v1/auth/register — Register a new user
- POST /api/v1/auth/login — Login user (returns access and refresh tokens)
- POST /api/v1/auth/refresh — Refresh access token using refresh token
- POST /api/v1/auth/logout — Logout user (invalidates tokens)

### Users
- GET /api/v1/users/me — Get current user information
- PUT /api/v1/users/me — Update current user information
- GET /api/v1/users/{user_id} — Get user by ID
- GET /api/v1/users/{user_id}/posts — Get posts by user (with pagination and sorting)

### Admin
- GET /api/v1/admin/users — Get all users (admin only)

### Posts
- POST /api/v1/posts — Create a new post
- GET /api/v1/posts — Get all posts (with filters, pagination, and sorting)
- GET /api/v1/posts/{post_id} — Get post by ID
- PUT /api/v1/posts/{post_id} — Update post (requires ownership)
- DELETE /api/v1/posts/{post_id} — Delete post (requires ownership)
- GET /api/v1/posts/user/{author_id} — Get posts by author (deprecated, use /api/v1/users/{user_id}/posts instead)
- POST /api/v1/posts/{post_id}/images — Upload post image
- GET /api/v1/posts/{post_id}/comments — Get comments for a post
- POST /api/v1/posts/{post_id}/comments — Create a comment on a post

### Comments
- PUT /api/v1/comments/{comment_id} — Update a comment (requires ownership)
- DELETE /api/v1/comments/{comment_id} — Delete a comment (requires ownership)

## Development

### Running Tests
_I'm disabling the warmings because there are some library warning. You definitely want to run the tests at some point with the warnings enabled._
```
pytest
pytest --cov --disable-warnings
pytest --cov --cov-report=html --disable-warnings
pytest -v --disable-warnings
```

### Testing endpoints with curl
```bash
# Register a new user
curl -X POST -H "Content-Type: application/json" -d '{ "email": "testuser@example.com", "password": "testpassword"}' http://localhost:8000/users/register

# Log in and get an access token
curl -X POST -H "Content-Type: application/json" -d '{"email": "testuser@example.com", "password": "testpassword"}' http://localhost:8000/auth/login

# Log in, get an access token, and store the token in an environment variable
TOKEN=$(curl -X POST -H "Content-Type: application/json" -d '{"email": "testuser@example.com", "password": "testpassword"}' http://localhost:8000/auth/login | jq -r '.access_token')

# Get current user information
curl -X GET -H "Authorization: Bearer $TOKEN" http://localhost:8000/users/me

# List all users (admin only)
curl -X GET -H "Authorization: Bearer $TOKEN" http://localhost:8000/admin/users

# Create a new blog post
curl -X POST -H "Content-Type: application/json" -d '{"title": "New Blog Post", "content": "This is the content of the new blog post."}' -H "Authorization: Bearer $TOKEN" http://localhost:8000/posts

# List all posts
curl -X GET http://localhost:8000/posts
```

### API Documentation
When the application is running, you can access:
- Interactive API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Alternative API documentation: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Project Structure
```
python-blog-backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # Application entry point
│   ├── auth.py          # Authentication logic
│   ├── crud.py          # Database operations
│   ├── database.py      # Database connection
│   ├── logger.py        # Logging configuration
│   ├── models.py        # Data models
│   ├── routes.py        # API endpoints
│   ├── schemas.py       # Pydantic schemas
│   └── tests/           # Test directory
│       ├── __init__.py
│       └── test_api.py  # API tests
├── Dockerfile           # Docker configuration
├── requirements.txt     # Python dependencies
└── README.md
```

## License

MIT

## Contributing

### Contribution Guidelines

We welcome contributions to improve this project! Please follow these steps:

1. **Fork the Repository**: Click the "Fork" button at the top of this repository to create your own copy.

2. **Clone Your Fork**:
   ```
   git clone https://github.com/pjbaur/python-blog-backend.git
   cd python-blog-backend
   ```

3. **Create a Branch**:
   ```
   git checkout -b feature/your-feature-name
   ```

4. **Make Your Changes**: Implement your feature or fix the issue.

5. **Run Tests**: Ensure all tests pass before submitting your changes:
   ```
   pytest
   ```

6. **Commit Your Changes**:
   ```
   git add .
   git commit -m "Add your descriptive commit message here"
   ```

7. **Push to Your Fork**:
   ```
   git push origin feature/your-feature-name
   ```

8. **Submit a Pull Request**: Open a pull request to the `main` branch of this repository. Provide a clear description of your changes.

### Code of Conduct

By contributing, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

Thank you for your contributions!
# Python Blog Backend API

A RESTful API backend for a blog application built with FastAPI and MongoDB.

## Features

- **User Authentication**: JWT-based authentication with secure password hashing
- **User Management**: Registration, login, and user profile endpoints
- **Password Security**: 
  - Password strength validation using zxcvbn
  - Password change functionality
  - Password history tracking to prevent reuse
- **Blog Post Management**: Create, read, update, and delete blog posts
- **Comment System**: Support for nested comments on blog posts with separate collection
- **Admin Panel**: Protected endpoints for administrative functions
- **Image Upload**: Support for uploading images for blog posts
- **Dockerized**: Easy deployment with Docker

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [MongoDB](https://www.mongodb.com/)
- **Authentication**: JWT tokens via [python-jose](https://github.com/mpdavis/python-jose) and [passlib](https://passlib.readthedocs.io/)
- **Password Strength**: [zxcvbn](https://github.com/dropbox/zxcvbn) for reliable password strength estimation
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

### Authentication
- POST /api/v1/auth/register — Register a new user
- POST /api/v1/auth/login — Login user (returns access and refresh tokens)
- POST /api/v1/auth/refresh — Refresh access token using refresh token
- POST /api/v1/auth/logout — Logout user (invalidates tokens)
- POST /api/v1/auth/change-password — Change user password (requires current password)

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

### Comments
- GET /api/v1/posts/{post_id}/comments — Get comments for a post
- POST /api/v1/posts/{post_id}/comments — Create a comment on a post
- PUT /api/v1/comments/{comment_id} — Update a comment (requires ownership)
- DELETE /api/v1/comments/{comment_id} — Delete a comment (requires ownership)
- POST /api/v1/comments/{comment_id}/replies — Create a reply to a comment

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

### TODO

- Improve password validation testing
- Improve CRUD testing
- Improve auth testing

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
│   ├── password_validation.py # Password strength and history validation
│   ├── routes.py        # Main API routes
│   ├── schemas.py       # Pydantic schemas
│   ├── routers/         # Modular API routers
│   │   ├── __init__.py
│   │   ├── admin.py     # Admin endpoints
│   │   ├── auth.py      # Auth endpoints
│   │   ├── comments.py  # Comment endpoints 
│   │   ├── posts.py     # Post endpoints
│   │   └── users.py     # User endpoints
│   └── tests/           # Test directory
│       ├── __init__.py
│       ├── test_admin_api.py
│       ├── test_auth_tokens.py
│       ├── test_comments.py
│       ├── test_crud.py
│       ├── test_password_change.py
│       ├── test_posts.py
│       ├── test_users.py
│       └── test_utils.py
├── changes/             # Change documentation
├── documentation/       # Project documentation
├── logs/                # Application logs
├── uploads/             # Uploaded files (images)
├── Dockerfile           # Docker configuration
├── requirements.txt     # Python dependencies
├── env.template         # Environment variables template
├── CODE_OF_CONDUCT.md   # Code of conduct
└── README.md
```

## Dependencies
- Install MinioClient locally: `pip install -e ../minio-client`

## Trade-offs

### Business Logic in Routes vs. Service Layer

This application places business logic directly within route handlers rather than using a dedicated service layer. This architectural decision has several implications:

#### Advantages
- **Simplicity**: For smaller applications, keeping logic in routes is straightforward
- **Development Speed**: Faster initial development due to less abstraction
- **Reduced Boilerplate**: Fewer files and less code organization needed
- **Easier to Understand**: New developers can see the full request-to-response flow in one place

#### Disadvantages
- **Reduced Testability**: Business logic mixed with HTTP concerns is harder to unit test
- **Code Duplication**: Similar business logic may be repeated across multiple route handlers
- **Maintainability Issues**: As the application grows, route files become bloated
- **Harder Refactoring**: Changing business rules requires touching HTTP-specific code

For a portfolio project like this one, this approach is acceptable, but for larger production applications, refactoring toward a service-oriented architecture would be beneficial for maintainability and testability.

### MongoDB vs SQL Database

This application uses MongoDB (NoSQL) instead of a relational database like PostgreSQL.

#### Advantages
- **Schema Flexibility**: Easy to evolve data models without migrations
- **JSON-Native Storage**: Natural fit for JSON-based APIs
- **Horizontal Scalability**: Easier sharding and distribution for high-volume data
- **Performance**: Fast reads and writes for document-centric operations

#### Disadvantages
- **Lack of ACID Transactions**: Limited transaction support compared to SQL databases
- **Denormalization**: May require duplicating data across documents
- **Query Complexity**: Complex joins and relationships are more difficult
- **Storage Efficiency**: Can be less space-efficient than normalized SQL data

The choice of MongoDB works well for a blog platform where document structure (posts, comments) naturally fits the document model, but a relational database might be better for highly relational data with complex joins.

### JWT Authentication Strategy

The application uses JWT tokens with refresh token functionality for authentication.

#### Advantages
- **Stateless Authentication**: No need to store session data server-side
- **Scalability**: Works well across distributed systems
- **Cross-Domain**: Easily used across different domains and services
- **Mobile Friendly**: Well-suited for mobile and API authentication

#### Disadvantages
- **Token Size**: JWTs can be larger than session IDs
- **Revocation Challenges**: Tokens remain valid until expiration unless additional invalidation measures are implemented
- **Secret Management**: Requires secure handling of signing keys
- **Token Storage**: Client-side storage requires careful security considerations

This authentication approach aligns well with the stateless nature of REST APIs, but session-based authentication might be simpler for smaller, monolithic applications.

### Monolithic Application vs Microservices

The application follows a monolithic architecture with modular components rather than microservices.

#### Advantages
- **Simplicity**: Easier development, deployment, and debugging
- **Performance**: No inter-service communication overhead
- **Consistency**: Shared code and models across the application
- **Development Speed**: Faster initial development and iteration

#### Disadvantages
- **Scalability Limitations**: All components must scale together
- **Technology Constraints**: Single technology stack for the entire application
- **Deployment Risk**: Changes to any part require redeploying the entire application
- **Team Coordination**: Can be challenging for larger teams working on different features

For this portfolio application, a monolithic approach provides simplicity and rapid development. Microservices would add unnecessary complexity unless there were specific scalability or team organization requirements.

### FastAPI Framework Choice

Using FastAPI instead of alternatives like Flask, Django, or Express.js.

#### Advantages
- **Performance**: High-speed API serving with Starlette and Uvicorn
- **Type Safety**: Built-in Pydantic data validation
- **OpenAPI Integration**: Automatic API documentation generation
- **Modern Python Features**: Async/await support and type hints

#### Disadvantages
- **Ecosystem Maturity**: Newer framework with smaller ecosystem than Django or Flask
- **Learning Curve**: Type annotations and async concepts may be unfamiliar
- **Limited Built-ins**: Fewer built-in features compared to full-stack frameworks like Django
- **Community Size**: Smaller community compared to more established frameworks

FastAPI's focus on API development with modern Python features makes it well-suited for this project, though Django might offer more built-in features and Rails-like development speed for full applications.

### Directory Structure and Code Organization

The application uses a router-based organization pattern.

#### Advantages
- **API-Focused Structure**: Clear organization around API endpoints
- **Separation by Domain**: Easy to find code related to specific features
- **Framework Alignment**: Follows FastAPI's recommended structure
- **Request-Centric**: Navigation correlates to API endpoints

#### Disadvantages
- **Business Logic Scattering**: Business logic can spread across multiple modules
- **Cross-Cutting Concerns**: Features that span multiple domains can be awkward
- **Route Coupling**: Routes may contain mixed concerns (validation, auth, business logic)
- **Growth Challenges**: May become unwieldy as application grows

This structure works well for an API-focused application but alternatives like domain-driven design might better separate business concerns as the application grows.

### Local File Storage for Images

Images are stored in the local filesystem rather than cloud storage solutions.

#### Advantages
- **Simplicity**: No external dependencies or configurations
- **Development Friendly**: Easy to set up and test locally
- **Cost**: No additional cloud storage costs
- **Control**: Complete control over the storage system

#### Disadvantages
- **Scalability Concerns**: Limited by local disk space
- **Reliability**: No built-in redundancy or backup
- **Distribution Challenges**: Harder to serve from CDNs or distribute geographically
- **Deployment Complexity**: Requires persistent volumes in containerized deployments

Local storage works for development and small deployments, but production applications would benefit from using S3 or similar cloud storage solutions for scalability and reliability.

### Error Handling Strategy

The application handles errors through HTTPExceptions and FastAPI's exception handling.

#### Advantages
- **Framework Integration**: Leverages FastAPI's built-in exception handling
- **HTTP Semantics**: Errors map cleanly to HTTP status codes
- **Simplicity**: Straightforward error raising and catching
- **Validation Integration**: Works well with Pydantic validation errors

#### Disadvantages
- **Limited Granularity**: HTTP status codes provide limited error type information
- **Error Consistency**: Error formats may vary across different parts of the application
- **Client Adaptability**: Clients need to handle various error formats
- **Debugging Information**: May include too much or too little information for debugging

This approach provides a good balance for a RESTful API, though more structured error objects with error codes might be beneficial for larger applications.

### Configuration Management

The application uses environment variables for configuration.

#### Advantages
- **Deployment Flexibility**: Easy to configure in different environments
- **Security**: Sensitive values kept out of source code
- **Docker Compatibility**: Works well with containerized deployments
- **Twelve-Factor Alignment**: Follows modern application design principles

#### Disadvantages
- **Type Safety**: Limited type checking for configuration values
- **Documentation**: Configuration options may not be self-documenting
- **Default Values**: Requires additional code for defaults and validation
- **Complex Configurations**: Limited structure for nested configurations

Environment variables provide a simple and effective configuration approach for this application, though structured configuration files might offer better organization for more complex applications.

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
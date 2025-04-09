**API Specification Document (OpenAPI 3.0.0)**  
```yaml
openapi: 3.0.0
info:
  title: Blog API
  version: 1.0.0
  description: Secure blog backend API for portfolio project
servers:
  - url: /v1
securitySchemes:
  BearerAuth:
    type: http
    scheme: bearer
    bearerFormat: JWT
components:
  securitySchemes:
    BearerAuth: []
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
          readOnly: true
        email:
          type: string
          format: email
        hashedPassword:
          type: string
          writeOnly: true
        createdOn:
          type: string
          format: date-time
          readOnly: true
        updatedOn:
          type: string
          format: date-time
          readOnly: true
        enabled:
          type: boolean
    Post:
      type: object
      properties:
        id:
          type: string
          format: uuid
          readOnly: true
        title:
          type: string
          minLength: 5
          maxLength: 100
        body:
          type: string
          maxLength: 10000
        categories:
          type: string
          maxLength: 255
        authorId:
          type: string
          format: uuid
          readOnly: true
        createdOn:
          type: string
          format: date-time
          readOnly: true
        updatedOn:
          type: string
          format: date-time
          readOnly: true
    Comment:
      type: object
      properties:
        id:
          type: string
          format: uuid
          readOnly: true
        body:
          type: string
          maxLength: 10000
        authorId:
          type: string
          format: uuid
          readOnly: true
        postId:
          type: string
          format: uuid
          readOnly: true
        createdOn:
          type: string
          format: date-time
          readOnly: true
        updatedOn:
          type: string
          format: date-time
          readOnly: true
    Error:
      type: object
      properties:
        message:
          type: string

paths:
  # Authentication
  /auth/register:
    post:
      tags: [Authentication]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email: 
                  $ref: '#/components/schemas/User/properties/email'
                password:
                  type: string
      responses:
        201:
          description: User registered
        400:
          $ref: '#/components/responses/ValidationError'

  /auth/login:
    post:
      tags: [Authentication]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email: 
                  $ref: '#/components/schemas/User/properties/email'
                password:
                  type: string
      responses:
        200:
          description: Returns JWT token
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token: 
                    type: string

  # Users
  /users:
    get:
      tags: [Users]
      security: [{BearerAuth: []}]
      responses:
        200:
          description: List all users
          content:
            application/json:
              schema:
                type: array
                items: 
                  $ref: '#/components/schemas/User'

  /users/{id}:
    put:
      tags: [Users]
      security: [{BearerAuth: []}]
      parameters:
        - name: id
          in: path
          required: true
          schema: 
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      responses:
        200:
          description: User updated

  /users/{id}/posts:
    get:
      tags: [Users]
      parameters:
        - name: id
          in: path
          required: true
          schema: 
            type: string
            format: uuid
      responses:
        200:
          description: Get user's posts
          content:
            application/json:
              schema:
                type: array
                items: 
                  $ref: '#/components/schemas/Post'

  # Posts
  /posts:
    get:
      tags: [Posts]
      responses:
        200:
          description: List all posts
          content:
            application/json:
              schema:
                type: array
                items: 
                  $ref: '#/components/schemas/Post'
    post:
      tags: [Posts]
      security: [{BearerAuth: []}]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [title, body]
              properties:
                title: 
                  $ref: '#/components/schemas/Post/properties/title'
                body: 
                  $ref: '#/components/schemas/Post/properties/body'
                categories: 
                  $ref: '#/components/schemas/Post/properties/categories'
      responses:
        201:
          description: Post created

  /posts/{id}:
    get:
      tags: [Posts]
      parameters:
        - name: id
          in: path
          required: true
          schema: 
            type: string
            format: uuid
      responses:
        200:
          description: Get post by ID
    put:
      tags: [Posts]
      security: [{BearerAuth: []}]
      parameters:
        - name: id
          in: path
          required: true
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Post'
      responses:
        200:
          description: Post updated
    delete:
      tags: [Posts]
      security: [{BearerAuth: []}]
      parameters:
        - name: id
          in: path
          required: true
      responses:
        204:
          description: Post deleted

  /posts/{id}/comments:
    get:
      tags: [Posts]
      parameters:
        - name: id
          in: path
          required: true
      responses:
        200:
          description: Get post comments
          content:
            application/json:
              schema:
                type: array
                items: 
                  $ref: '#/components/schemas/Comment'

  # Comments
  /comments:
    post:
      tags: [Comments]
      security: [{BearerAuth: []}]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [body]
              properties:
                body: 
                  $ref: '#/components/schemas/Comment/properties/body'
                postId:
                  type: string
                  format: uuid
      responses:
        201:
          description: Comment created

components:
  responses:
    ValidationError:
      description: Validation error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
```

---

**Resource Relationships**  
```
User (1) --< Post (n)
User (1) --< Comment (n)
Post (1) --< Comment (n)
```

---

**Key Endpoints**  
| Resource  | Method | Path                     | Description                 |
|-----------|--------|--------------------------|-----------------------------|
| Auth      | POST   | /v1/auth/register        | Register user               |
| Auth      | POST   | /v1/auth/login           | Login (JWT token)           |
| Users     | GET    | /v1/users                | List all users (Admin only) |
| Users     | PUT    | /v1/users/{id}           | Enable/disable user         |
| Posts     | GET    | /v1/posts                | List all posts              |
| Posts     | POST   | /v1/posts                | Create post                 |
| Posts     | PUT    | /v1/posts/{id}           | Update post                 |
| Comments  | POST   | /v1/comments             | Create comment              |

---

**Status Code Guidelines**  
- `200 OK`: Successful GET/PUT  
- `201 Created`: Resource created (POST)  
- `204 No Content`: Successful DELETE  
- `400 Bad Request`: Invalid request body  
- `401 Unauthorized`: Missing/invalid JWT  
- `403 Forbidden`: Insufficient permissions  
- `404 Not Found`: Resource doesn't exist  
- `500 Internal Server Error`: Unhandled exception  

---

**Versioning Strategy**  
- URI path versioning (`/v1/...`)  
- New versions will increment path (e.g., `/v2/...`)  
- No deprecation policy for MVP (post-MVP: 12-month sunset period)
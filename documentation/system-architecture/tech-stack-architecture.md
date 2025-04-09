# Technology Stack & Architecture Decisions

## Overview
This document outlines the key technology decisions and overall architecture for the Blog API project.

## Core Technology Stack

### Backend
- **Language/Framework**: Python with FastAPI
  - *Rationale*: FastAPI provides modern async capabilities, excellent performance, automatic OpenAPI documentation, and type validation with minimal boilerplate code.
- **Database**: PostgreSQL
  - *Rationale*: Reliable relational database with excellent support for JSON, full-text search capabilities, and strong data integrity features.
- **Authentication**: JWT-based authentication
  - *Rationale*: Stateless authentication that works well with REST APIs and facilitates future mobile integration.
- **Image Storage**: S3-compatible storage
  - *Rationale*: Separates image storage from application code, provides scalability, and easy migration path to AWS S3 in the future.

### Infrastructure
- **Deployment**: Docker containers
  - *Rationale*: Provides consistency between development and production environments, simplifies dependency management.
- **Hosting**: Self-hosted initially
  - *Rationale*: Meets current requirements while keeping costs controlled for a portfolio project.

## Key Architecture Decisions

### 1. Monolithic API Structure
**Decision**: Implement as a single, modular API service rather than microservices.

**Rationale**:
- Simplifies development and deployment for a portfolio project
- Appropriate for the expected low traffic volume
- Easier to reason about and demonstrate as a portfolio piece
- Can be refactored into microservices later if needed

### 2. Database-Native Full-Text Search
**Decision**: Utilize PostgreSQL's built-in full-text search capabilities.

**Rationale**:
- Avoids introducing additional infrastructure components
- PostgreSQL's full-text search is sufficient for the expected data volume and query complexity
- Simplifies the architecture
- Provides a clear migration path to Elasticsearch if needed in the future

### 3. Role-Based Access Control
**Decision**: Implement RBAC with two primary roles (ADMIN, AUTHOR) plus anonymous access.

**Rationale**:
- Provides clear permission boundaries
- Simplifies authorization logic
- Matches the application's user interaction model
- Extensible for future role additions

### 4. Standard REST API Design
**Decision**: Follow REST principles with JSON payloads.

**Rationale**:
- Well-understood by frontend developers
- Compatible with chosen technology stack
- Suitable for both web and future mobile clients
- Facilitates demonstration as a portfolio project

### 5. Threaded Comments Implementation
**Decision**: Store comments with parent-child relationships in the database.

**Rationale**:
- Allows for nested comment display
- Provides efficient retrieval of comment threads
- Can be implemented cleanly in a relational database

## Considerations for Future Expansion

### Potential Future Components
- **Elasticsearch**: For advanced search if PostgreSQL search becomes insufficient
- **Redis**: For caching frequently accessed content
- **Background Workers**: For scheduled publishing and other async tasks
- **CDN Integration**: For image delivery optimization if traffic increases

### API Versioning Strategy
- Use URL-based versioning (e.g., `/api/v1/`) to allow for non-breaking changes in the future
- Document clear deprecation policies for future API versions

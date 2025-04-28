Do not make any changes. Review documentation/system-architecture/architectural-artifacts.md. Is the application accurately following the architectural-artifacts.md? Are there discrepancies? If so, give me details.

(Claude 3.7 Sonnet) I'll review the `architectural-artifacts.md` document against the actual implementation of your Python blog backend application to identify any discrepancies.

After analyzing the architecture document and the actual codebase, I've found several discrepancies between what was planned in the architecture document and what was actually implemented:

## Major Discrepancies

### 1. Database Technology
- **Architecture Document**: Specifies PostgreSQL as the database
- **Actual Implementation**: Uses MongoDB (evident from imports and database operations in crud.py)

### 2. Component Architecture
- **Architecture Document**: Shows separate components for Search Management, Tags & Categories Handler
- **Actual Implementation**: No dedicated search endpoint exists, and there's no implementation for categories management endpoints

### 3. Unimplemented Endpoints
Several endpoints specified in the architecture document don't exist in the implementation:
- No `/api/v1/categories` endpoints (GET, POST, PUT, DELETE)
- No `/api/v1/search` endpoint
- No `/api/v1/hashtags` endpoints

### 4. Image Storage
- **Architecture Document**: Specifies S3-compatible storage
- **Actual Implementation**: Uses local filesystem storage (in "uploads/images" directory)

### 5. Data Model
- **Architecture Document**: Shows tables for CATEGORIES, POST_CATEGORIES, HASHTAGS, POST_HASHTAGS
- **Actual Implementation**: These are not implemented as separate collections in MongoDB

## Minor Discrepancies

### 1. Authentication Flow
- **Architecture Document**: Shows a dedicated Token Service component
- **Actual Implementation**: Token handling is integrated directly into the auth.py module

### 2. Endpoint Paths
Some endpoints have slight differences in structure compared to what was documented:
- The architecture document has `/api/v1/auth/register` but the actual implementation has both `/api/v1/auth/register` and `/api/v1/users/register` with the former being the current active endpoint

### 3. Comments Implementation
- **Architecture Document**: Shows a threaded comment structure with parent-child relationships
- **Actual Implementation**: Does implement threaded comments, but the specific schema and implementation details differ somewhat from what was documented

### 4. Non-Functional Requirements
Several non-functional requirements mentioned in the document don't have visible implementation:
- Rate limiting for invalid login attempts
- HTTPS enforcement (though this is often handled at the deployment level)
- Automated backups

## Summary

The application follows the general structure of what was planned in the architectural artifacts document, particularly in terms of:
- Using a monolithic but modular API structure
- Implementing JWT-based authentication
- Following REST principles with JSON
- Implementing role-based access control

However, there are significant differences in the core technology choices (MongoDB vs PostgreSQL) and several planned features and endpoints that are not implemented in the current codebase. The document appears to have been created as an architectural plan that wasn't fully followed during implementation, or it represents a future vision for the application that hasn't been completely realized yet.
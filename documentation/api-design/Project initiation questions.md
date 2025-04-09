REST API Project Initiation Questionnaire  

This questionnaire is designed to gather critical information to design and document a REST API effectively. Use it to align stakeholders, clarify requirements, and ensure all aspects of the API are considered.  

---

I. Project Overview
1. What is the **primary purpose** of the API?  
2. Who are the **target users** (e.g., internal teams, external developers, partners)?  
3. Are there existing systems or APIs this API must **integrate with**? List them.  
4. Who are the **key stakeholders** (technical and non-technical)?  

---

II. Functional Requirements
5. What **core operations** must the API support (e.g., CRUD, search, batch processing, file uploads)?  
6. Are there **asynchronous operations** (e.g., long-running tasks requiring polling or webhooks)?  
7. Are there **bulk operations** (e.g., create/update multiple resources in one request)?  
8. Does the API need to support **partial updates** (e.g., PATCH vs. PUT)?  

---

III. Resource Modeling
9. List all **core resources** (e.g., `User`, `Order`, `Product`) and their attributes (name, data type, constraints).  
10. Describe **relationships** between resources (e.g., one-to-many, many-to-many).  
11. Are there **sub-resources** (e.g., `/orders/{id}/items`)?  
12. Are any attributes **read-only**, computed, or derived (e.g., `created_at`, `total_price`)?  
13. What **data validation rules** apply (e.g., regex for email, min/max length)?  

---

IV. Endpoint Design & URL Structure
14. What **HTTP methods** (GET, POST, etc.) will each endpoint support?  
15. What **URL naming conventions** will be used (e.g., plural nouns, lowercase)?  
16. How will **path parameters** be formatted (e.g., `/users/{id}` vs. `/users/:id`)?  
17. Should endpoints support **filtering**, **sorting**, or **pagination**? Specify syntax (e.g., `?sort=name&filter=active`).  
18. Will **HATEOAS** (hypermedia links in responses) be required?  

---

V. Request/Response Schemas
19. What **data formats** are supported (JSON, XML, etc.)?  
20 What **headers** are required (e.g., `Authorization`, `Accept`, `Content-Type`)?  
21. Are there **mandatory fields** for requests? Are fields conditionally required?  
22. How will **versioning** be reflected (e.g., `Accept: application/vnd.myapi.v1+json`)?  
23. Should responses include **envelope structures** (e.g., `{ "data": {}, "meta": {} }`)?  

---

VI. Error Handling & Status Codes
24. Which **HTTP status codes** will be used for common scenarios (e.g., 200, 201, 400, 404, 429, 500)?  
25. What **error response schema** will be used (e.g., `{ "code": "404", "message": "..." }`)?  
26. Are there **custom error codes** for business logic failures?  
27. How will **rate limiting** be communicated (e.g., `Retry-After` header)?  

---

VII. Security Requirements
28. What **authentication** method will be used (e.g., OAuth2, API keys, JWT)?  
29. Are there **authorization** rules (e.g., roles, scopes, RBAC)?  
30. Will the API require **encryption** (e.g., HTTPS, mutual TLS)?  
31. Are there **rate limiting** or throttling policies (e.g., 1000 requests/hour)?  
32. How will **sensitive data** (e.g., PII) be handled?  

---

VIII. Versioning Strategy
33. What **versioning method** will be used (e.g., URL path `/v1/...`, headers, query params)?  
34. What is the policy for **deprecating** endpoints (e.g., sunset headers, documentation notices)?  
35. How will **breaking changes** be communicated to consumers?  

---

IX. Non-Functional Requirements
36. What are **performance SLAs** (e.g., 95% of requests < 500ms)?  
37. What **uptime/availability** is required (e.g., 99.9%)?  
38. Are there **compliance requirements** (e.g., GDPR, HIPAA)?  
39. What **monitoring/logging** tools will be integrated (e.g., Prometheus, OpenTelemetry)?  

---

X. Documentation & Tooling
40. What **tools** will be used for documentation (e.g., Swagger UI, Redoc, ReadMe)?  
41. Are **client SDKs** or code samples needed (e.g., Python, JavaScript)?  
42. Will a **developer portal** be required for onboarding?  

---

XI. Testing & Deployment
43. What **environments** will be used (e.g., dev, staging, prod)?  
44. Are there **mock API** requirements for testing?  
45. What **CI/CD pipeline** tools will be used (e.g., GitHub Actions, Jenkins)?  
46. How will **rollbacks** be handled if a release fails?  

---

### Next Steps  
1. Review answers with stakeholders to resolve ambiguities.  
2. Use responses to draft the **OpenAPI specification** and **resource models**.  
3. Define **versioning** and **security policies** based on requirements.  
4. Iterate on the questionnaire for future projects.  

This ensures alignment and provides a foundation for scalable, maintainable API design.

---

# Answers

I. Project Overview
1. What is the **primary purpose** of the API?
- This REST API creates the backend of a secure blog application.
2. Who are the **target users** (e.g., internal teams, external developers, partners)?
- This is a personal project for a portfolio.
3. Are there existing systems or APIs this API must **integrate with**?
- No
4. Who are the **key stakeholders** (technical and non-technical)?
- I am the sole stakeholder.

---

II. Functional Requirements
5. What **core operations** must the API support (e.g., CRUD, search, batch processing, file uploads)?
- Register new user
- Log in
- Log out
- View all blog entries
- View a blog entry
- View comments for a blog entry
- Create a blog entry
- Edit a blog entry
- Delete a blog entry
- View all users
- Disable a user
- Enable a user
6. Are there **asynchronous operations** (e.g., long-running tasks requiring polling or webhooks)?
- No
7. Are there **bulk operations** (e.g., create/update multiple resources in one request)?
- No
8. Does the API need to support **partial updates** (e.g., PATCH vs. PUT)?
- No.

---

III. Resource Modeling
9. List all **core resources** (e.g., `User`, `Order`, `Product`) and their attributes (name, data type, constraints).
- Post
  - Id
  - Title
  - Body
  - Categories
  - Author
  - CreatedOn
  - UpdatedOn
- Comment
  - Id
  - Body
  - Author
  - CreatedOn
  - UpdatedOn
- User
  - Id
  - Email
  - HashedPassword
  - CreatedOn
  - UpdatedOn
  - Enabled
10. Describe **relationships** between resources (e.g., one-to-many, many-to-many).
- A User can have many Posts.
- A User can have many Comments.
- A Post can have many Comments.
11. Are there **sub-resources** (e.g., `/orders/{id}/items`)?
- /users/{id}/posts
- /posts/{id}/comments
12. Are any attributes **read-only**, computed, or derived (e.g., `created_at`, `total_price`)?
- CreatedOn: computed, read-only
- UpdatedOn: computed, read-only
13. What **data validation rules** apply (e.g., regex for email, min/max length)?  
- Email: regex
- Title: min 5 chars/max 100 chars
- Body: max 10000 chars
- Categories: max 255 chars
---

IV. Endpoint Design & URL Structure
14. What **HTTP methods** (GET, POST, etc.) will each endpoint support?
- BlogPost: GET, POST, PUT, DELETE
- Comment: GET, POST, PUT, DELETE
- User: GET, POST, PUT
15. What **URL naming conventions** will be used (e.g., plural nouns, lowercase)?
- Follow best practices
16. How will **path parameters** be formatted (e.g., `/users/{id}` vs. `/users/:id`)?
- Follow best practices and framework (FastAPI) guidelines
17. Should endpoints support **filtering**, **sorting**, or **pagination**? Specify syntax (e.g., `?sort=name&filter=active`).
- Yes. Implement in phases post-MVP
18. Will **HATEOAS** (hypermedia links in responses) be required?  
- If possible, implement post-MVP

---

V. Request/Response Schemas
19. What **data formats** are supported (JSON, XML, etc.)?  
- JSON
20 What **headers** are required (e.g., `Authorization`, `Accept`, `Content-Type`)?
- Standard headers, whatever is required by framework (FastAPI) and JWT
21. Are there **mandatory fields** for requests? Are fields conditionally required?
- Fields are passed as JSON in the body.
- Post: Title and Body are required. Categories is optional.
- Comment: Body is required.
22. How will **versioning** be reflected (e.g., `Accept: application/vnd.myapi.v1+json`)?  
- URI versioning
23. Should responses include **envelope structures** (e.g., `{ "data": {}, "meta": {} }`)?  
- Use standard HTTP Headers for pagination, rate limits, errors, etc. Fully document the choices and implementation.
---

VI. Error Handling & Status Codes
24. Which **HTTP status codes** will be used for common scenarios (e.g., 200, 201, 400, 404, 429, 500)?
- Follow standards and best practices. Fully document the choices made.
25. What **error response schema** will be used (e.g., `{ "code": "404", "message": "..." }`)?
- Use whatever the current best practices are.
26. Are there **custom error codes** for business logic failures?
- No
27. How will **rate limiting** be communicated (e.g., `Retry-After` header)?
- Use current best practice using headers.  

---

VII. Security Requirements
28. What **authentication** method will be used (e.g., OAuth2, API keys, JWT)?  
- JWT
29. Are there **authorization** rules (e.g., roles, scopes, RBAC)?
- The application has two roles: ADMIN, AUTHOR  
30. Will the API require **encryption** (e.g., HTTPS, mutual TLS)?
- Implement post-MVP.
31. Are there **rate limiting** or throttling policies (e.g., 1000 requests/hour)?
- Not in MVP. Implement in a later phase.
32. How will **sensitive data** (e.g., PII) be handled?
- No sensitive data. Passwords are hash using current best practices.

---

VIII. Versioning Strategy
33. What **versioning method** will be used (e.g., URL path `/v1/...`, headers, query params)?
- URL path  
34. What is the policy for **deprecating** endpoints (e.g., sunset headers, documentation notices)?  
- Use best practices, implement post-MVP.
35. How will **breaking changes** be communicated to consumers?  
- Implement notice/news banner on home page, post-MVP.

---

IX. Non-Functional Requirements
36. What are **performance SLAs** (e.g., 95% of requests < 500ms)?
- N/A  
37. What **uptime/availability** is required (e.g., 99.9%)?
- Implement HA in later phase.
38. Are there **compliance requirements** (e.g., GDPR, HIPAA)?  
- No
39. What **monitoring/logging** tools will be integrated (e.g., Prometheus, OpenTelemetry)?  
- N/A

---

X. Documentation & Tooling
40. What **tools** will be used for documentation (e.g., Swagger UI, Redoc, ReadMe)?
- OpenAPI/Swagger UI
41. Are **client SDKs** or code samples needed (e.g., Python, JavaScript)?
- No
42. Will a **developer portal** be required for onboarding?
- No

---

XI. Testing & Deployment
43. What **environments** will be used (e.g., dev, staging, prod)?
- For MVP, just the development environment. Staging and Prod can be implemented in later phases.
44. Are there **mock API** requirements for testing?
- Yes, if appropriate.
45. What **CI/CD pipeline** tools will be used (e.g., GitHub Actions, Jenkins)?
- GitHub, Jenkins. Jenkins will poll Github.
46. How will **rollbacks** be handled if a release fails?
- TBD. Implement Post-MVP.  

---

# ChatGPT

Below are a few clarifying questions before I produce the full set of design documents:

1. **Role-based access:** For endpoints that modify or disable resources, should we enforce that only users with the ADMIN role can disable or enable users, and only ADMIN/AUTHOR roles can create/edit posts?  
2. **Token management:** In the authentication flow, do you require a token refresh mechanism, or is issuing a standard JWT (with an expiration) sufficient for this MVP?  
3. **Filtering, sorting, and pagination:** Although these features are planned for post-MVP, do you have any preferred parameter names or formats (e.g., `page`, `limit`, `sort_by`) that we should document now as part of our future-proof design?  
4. **HATEOAS links:** For the MVP documentation, would you like to include notes on HATEOAS as “planned” features, or should we leave them out entirely until post-MVP?  
5. **Error response schema:** You mentioned a simple structure with code and message. Would you prefer this to be just a two-field JSON object, or would you like to include additional information (e.g., timestamp, error details) in our documented schema?

Once I have your feedback on these points, I can proceed with producing the following documents:

- **API Specification Document (OpenAPI/Swagger)**
- **Resource Models and Relationships**
- **Endpoint Definitions and URL Structures**
- **Request/Response Schemas**
- **Status Code Usage Guidelines**
- **Versioning Strategy Documentation**

Please let me know your thoughts on these clarifying questions.

## My answers

1. **Role-based access:** For endpoints that modify or disable resources, should we enforce that only users with the ADMIN role can disable or enable users, and only ADMIN/AUTHOR roles can create/edit posts?  
- Correct
2. **Token management:** In the authentication flow, do you require a token refresh mechanism, or is issuing a standard JWT (with an expiration) sufficient for this MVP?  
For MVP, let's use standard JWT. In later phases we can implement refresh and log out (with token invalidation)
3. **Filtering, sorting, and pagination:** Although these features are planned for post-MVP, do you have any preferred parameter names or formats (e.g., `page`, `limit`, `sort_by`) that we should document now as part of our future-proof design?  
- I have no preferences, and defer to current best-practices.
4. **HATEOAS links:** For the MVP documentation, would you like to include notes on HATEOAS as “planned” features, or should we leave them out entirely until post-MVP?  
- We can include notes, but we'll implement post-MVP.
5. **Error response schema:** You mentioned a simple structure with code and message. Would you prefer this to be just a two-field JSON object, or would you like to include additional information (e.g., timestamp, error details) in our documented schema?
- Just the simple two-field JSON object. A: I don't want to expose system information. B: We'll log the timestamp and error details.

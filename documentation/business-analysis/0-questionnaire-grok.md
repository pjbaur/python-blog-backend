### **Blog Application REST API Backend Project Questionnaire**

#### **Section 1: Business Requirements**
This section collects high-level information about the project's purpose, audience, and goals to inform the Business Requirements Document (BRD).

1. **What is the primary purpose of the blog application?**  
   _(e.g., to provide a platform for content sharing, to build a community, to generate revenue through content)_  
   - This is a personal project that I will use to showcase my skills to potential employers.
2. **Who is the target audience for the blog?**  
   _(e.g., general readers, niche content enthusiasts, content creators, administrators)_  
   - It will be a general use blog.
3. **What are the key business objectives that the blog application should achieve?**  
   _(e.g., increase user engagement, drive traffic, establish thought leadership)_  
   - Showcase my project management, business analysis, software architecture, software engineering, and development skills. It will also show my technical skills in related platforms, technologies, etc.
4. **Are there any specific constraints or assumptions we should be aware of?**  
   _(e.g., budget limitations, timeline, preferred technology stack, compliance requirements)_  
   - This is a personal project. I am the sole person involved. 
   - It will be hosted locally in one environment.
   - In later phases I'll create staging and production environments, as well as cloud hosting.
   - I want to use Python and FastAPI with PostgreSQL, and use Docker for containerization.
   - In later projects I will implement GraphQL, and build parallel systems using other platforms including Node.js/NextJS, Java/Spring, and Go/Gin.

---

#### **Section 2: Functional Requirements**
This section gathers details about the core features and functionalities needed for the Functional Requirements Specification (FRS).

5. **What are the essential features the blog application must have?**  
   _(e.g., creating and publishing posts, commenting, user management, search functionality)_  
   - creating and publishing posts, commenting, user management. For post-MVP: Search, dashboard/statistics, Post Series, Threaded commenting, backup, archiving, likes, hashtagging, categories, comment moderation
6. **Are there any specific requirements for user authentication and authorization?**  
   _(e.g., email/password login, social media login, role-based access control)_  
   - email/password login
   - JWT
   - RBAC [Author|Admin]
   - For post-MVP: social media login, API key
7. **How should the application handle different user roles? What permissions should each role have?**  
   _(e.g., readers can view and comment, authors can create/edit posts, administrators can manage users)_  
   - Anonymous users can view
   - Logged in users can post and comment, and can edit/delete their own posts/comments
   - Administrators can manage users and can edit/delete all posts/comments
   - Post-MVP: Comment moderators
8. **What functionalities are needed for managing blog posts?**  
   _(e.g., creating, editing, deleting, publishing, scheduling, archiving)_  
   - Creating, Editing, Deleting
   - Post-MVP: Drafts, Archiving, Comment moderation
9. **How should comments be managed?**  
   _(e.g., moderation, replying, nesting, spam filtering, approval workflows)_  
   - Any logged in user can comment on any post.
   - Post-MVP: Threaded comments, moderation
10. **Are there any specific requirements for content management?**  
    _(e.g., tagging, categorization, search by keyword or tag, rich text editing)_  
    - Post-MVP: hashtags in content, categorization, search by keyword or tag
11. **Does the application need to integrate with any external systems or APIs?**  
    _(e.g., social media sharing, email notifications, third-party analytics tools)_  
    - Post-MVP: statistics, web analytics

---

#### **Section 3: User Interactions**
This section identifies user roles and their interactions with the system to support Use Case Diagrams, Descriptions, and User Stories.

12. **Can you describe the different types of users who will interact with the blog application?**  
    _(e.g., anonymous readers, registered readers, authors, moderators, administrators)_  
    - anonymous readers, registered readers, authors, administrators
13. **For each user type, what are the main actions they will perform?**  
    _(e.g., readers can view posts and comment, authors can create and edit posts, admins can delete users)_  
    - Anonymous users can read any post or comment
    - Logged in users can create/edit/delete their own posts and comments.
    - Admins can inactivate users, edit/delete any post/comment
14. **Are there any specific scenarios or workflows that are critical for the application?**  
    _(e.g., publishing a post with approval, moderating a comment before it goes live)_  
    - N/A
15. **Can you provide examples of user stories from the perspective of different users?**  
    _(e.g., "As a reader, I want to search for posts by keyword so that I can find relevant content")_  
    ## User Stories for the Blog Application

    ### Reader Stories
    These stories are for users who visit the blog to consume content. They may be anonymous or registered users without additional privileges.

    1. **As a reader, I want to view the latest blog posts** so that I can stay updated on new content.
    2. **As a reader, I want to search for posts by keyword** so that I can find relevant articles.
    3. **As a reader, I want to filter posts by category** so that I can explore topics of interest.
    4. **As a reader, I want to read individual posts** so that I can consume the full content.
    5. **As a reader, I want to view comments on posts** so that I can see discussions.

    ### Registered Reader Stories
    These stories apply to readers who have created an account, unlocking additional features like commenting and subscribing.

    6. **As a registered reader, I want to leave comments on posts** so that I can share my thoughts.
    7. **As a user, I want to register for an account** so that I can access additional features.
    8. **As a user, I want to log in to my account** so that I can access my personalized settings.
    9. **As a user, I want to reset my password** if I forget it.

    ### Author Stories
    These stories are for content creators who write and manage blog posts.

    10. **As an author, I want to create new blog posts** so that I can share my ideas.
    11. **As an author, I want to edit my own posts** so that I can correct mistakes or update information.
    12. **As an author, I want to delete my own posts** if they are no longer relevant.

    ### Administrator Stories
    These stories are for users who manage the overall application, including user accounts and system settings.

    13. **As an administrator, I want to manage user accounts** so that I can control access to the application.
    14. **As an administrator, I want to restore deleted posts** if they were removed by mistake.

    ### Technical/System Stories
    These stories ensure the application meets quality attributes (e.g., performance, security) and supports developers building the frontend.

    15. **As a user, I want the application to load quickly** so that I can access content without delay.
    16. **As a user, I want the application to be secure** so that my data is protected.
    17. **As a developer, I want the API to provide endpoints for creating, reading, updating, and deleting posts** so that I can build a dynamic frontend.
    18. **As a developer, I want the API to support pagination for listing posts** so that I can handle large amounts of data efficiently.
    19. **As a developer, I want the API to return appropriate error codes and messages** so that I can handle exceptions gracefully.


---

#### **Section 4: Data Requirements**
This section defines the data entities, attributes, and relationships to inform the Data Requirements and database design.

16. **What are the main data entities the application needs to handle?**  
    _(e.g., posts, comments, users, categories, tags)_  
17. **What attributes should each entity have?**  
    _(e.g., post: title, content, author, publish date, status; comment: text, author, timestamp)_  
18. **How are these entities related to each other?**  
    _(e.g., a post has many comments, a user can author many posts, a post belongs to multiple categories)_  

---

#### **Section 5: Non-Functional Requirements**
This section addresses quality attributes like performance, security, and scalability for the Non-Functional Requirements.

19. **What are the performance expectations for the application?**  
    _(e.g., API response time under 200ms, support for 1,000 concurrent users)_  
    - API response time under 500ms, support for 10 concurrent users
20. **What security measures are required?**  
    _(e.g., HTTPS, data encryption, secure authentication, protection against SQL injection)_  
    - secure authentication, protection against SQL injection
    - Post-MVP: HTTPS
21. **Are there any scalability requirements?**  
    _(e.g., ability to handle 10,000 posts or 100,000 users over time)_  
    - Post-MVP, we'll add horizontal scaling with Docker Swarm or Kubernetes
22. **What are the usability expectations for the API?**  
    _(e.g., clear and concise documentation, intuitive endpoint design)_  
    - clear and concise documentation, intuitive endpoint design
23. **Are there any compliance or regulatory requirements the application must meet?**  
    _(e.g., GDPR for user data, CCPA, accessibility standards like WCAG)_  
    - No

---

#### **Section 6: API Specification**
This section collects initial requirements for the API design to create a draft API Specification.

24. **Do you have any preferences or requirements for the API design?**  
    _(e.g., RESTful principles, specific naming conventions, CRUD operations)_  
    - RESTful principles
25. **What data formats should the API use for requests and responses?**  
    _(e.g., JSON, XML, or both)_  
    - JSON
26. **How should authentication be handled in the API?**  
    _(e.g., JWT tokens, OAuth 2.0, API keys)_  
    - JWT tokens.
    - Post-MVP: Tokens can be invalidated when a user logs out. Tokens would be stored in the database. Expired tokens would be periodically purged from the database.
27. **Is there a need for versioning the API, and if so, how should it be implemented?**  
    _(e.g., in the URL like /v1/, via headers)_  
    - Yes, URL like /v1/
28. **Are there any specific error handling or logging requirements for the API?**  
    _(e.g., standard error codes, detailed logs for debugging)_  
    - standard error codes, detailed logs for debugging

---

#### **Section 7: Design and Documentation**
This section addresses visual design and documentation needs, potentially including Wireframes, Mockups, and a Glossary of Terms.

29. **Are there any existing designs or mockups for the frontend that we should consider when designing the API?**  
    _(e.g., sketches, prototypes, or existing UI designs)_  
    - Not yet, these will be created by the UX Designer.
30. **If no designs exist, would you like us to create wireframes or mockups to visualize how the data will be presented?**  
    _(e.g., simple layouts for post pages, comment sections)_  
    - Yes, please create wireframes and mockups to visualize how the data will be presented
31. **What are the expectations for API documentation and developer support?**  
    _(e.g., Swagger/OpenAPI spec, example requests/responses, SDKs)_  
    - Swagger/OpenAPI spec, example requests/responses

---

#### **Section 8: Project Management**
This section focuses on tracking and managing the project, supporting the Traceability Matrix, Change Management Plan, and Risk Assessment.

32. **How would you like to track the implementation of requirements?**  
    _(e.g., a traceability matrix linking requirements to use cases and test cases)_  
    - Yes
33. **What is the process for requesting, reviewing, and approving changes to the requirements?**  
    _(e.g., formal change request forms, approval by a steering committee)_  
    - Since this is a personal project, I am the only person involved. I am using a Kanban board.
34. **How should we handle changes that impact the project scope, timeline, or budget?**  
    _(e.g., escalation process, impact analysis)_  
    - Understanding this is a personal project, I am open to suggestions on how to handle changes.
35. **What potential risks do you foresee for this project?**  
    _(e.g., technical debt, resource availability, third-party API reliability)_  
    - Scope creep
36. **How would you like us to mitigate these risks?**  
    _(e.g., prototyping, contingency budget, regular risk reviews)_  
    - Need to keep tasks small and able to be completed by me in less than one week (preferrably one to two days).

---

#### **Section 9: Additional Considerations**
This section captures any additional requirements or preferences not covered above.

37. **Are there any specific deployment and hosting preferences?**  
    _(e.g., AWS, Azure, Google Cloud, on-premises, Docker containers)_  
    - On prem Docker containers
    - Post-MVP: AWS
38. **Is there a need for analytics or reporting features within the application?**  
    _(e.g., tracking post views, user activity, comment engagement)_  
    - Post-MVP: tracking post views, user activity, comment engagement, etc
39. **Are there any specific accessibility requirements for the application?**  
    _(e.g., WCAG 2.1 compliance for frontend integration)_  
    - Post-MVP
40. **Are there any other requirements, preferences, or considerations that we should be aware of?**  
    _(e.g., future expansion plans, specific vendor preferences)_  
    - Future plans have been mentioned throughout this document.

---

### **Instructions for Use**
- **Who should complete this questionnaire?**  
  Key stakeholders, such as product owners, business managers, technical leads, and any other individuals with insights into the project’s goals and requirements.  
- **How to answer:**  
  Provide detailed responses where possible. If a question does not apply, please note “N/A” or “To be determined.” Examples or clarifications are encouraged to ensure accuracy.  
- **Next steps:**  
  Once completed, the Business Analyst will use your responses to develop the necessary project documentation, including the BRD, FRS, Use Cases, and API Specification, ensuring alignment with your vision and needs.

---

This questionnaire is designed to be thorough yet user-friendly, enabling stakeholders to provide the information needed to produce high-quality documentation for the blog application's REST API backend. By addressing business goals, functional and non-functional requirements, user interactions, data needs, API design, and project management, it ensures a solid foundation for the project’s success.
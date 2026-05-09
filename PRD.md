# PRD
## Description
This PRD describes an MVP REST API for a Todo List application built with Python FastAPI and SQLite. Users can register and authenticate, then manage their personal tasks: create, view, mark as completed, and delete. The API returns JSON responses and uses token-based authentication (JWT) for secure access.
## Features
- User registration with email and password
- User login returning a JWT token
- Create a new task (title, description, due date optional)
- List all tasks for the authenticated user
- Update task completion status (mark as done/undone)
- Delete a task
- Basic error handling and input validation
## Success Criteria
- All endpoints return correct HTTP status codes (200, 201, 401, 404, etc.)
- Non-authenticated requests are rejected with 401
- Users can only access their own tasks
- CRUD operations work as expected in automated tests
- API documentation (auto-generated via FastAPI) is available at /docs
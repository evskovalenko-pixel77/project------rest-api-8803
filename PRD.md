# PRD
## Description
A REST API for managing a personal Todo list. Users can register, create tasks, mark them as completed, and delete tasks. Built with Python FastAPI and SQLite for persistence. Minimal authentication via API tokens.
## Features
- User registration and token-based authentication
- Create a task with title and description
- List all tasks for the authenticated user (with status)
- Mark a task as completed
- Delete a task
- Data persisted in SQLite database
- Auto-generated Swagger UI documentation
## Success Criteria
- All endpoints return correct HTTP status codes (200, 201, 401, 404, etc.)
- Users can only access and modify their own tasks
- Data survives server restart (SQLite file)
- Authentication token is required for task operations
- API documentation is accessible at /docs
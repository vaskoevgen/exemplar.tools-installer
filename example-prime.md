# Todo List API

Build a simple REST API for managing todo tasks.

## What to build

A Python HTTP service that stores todo items and exposes a REST API.

## Endpoints

- GET /tasks — return all tasks as a JSON list, each with id, title, completed, and created_at fields
- POST /tasks — create a new task from a JSON body with a title field, return the created task
- PUT /tasks/id — update a task by id, accept title and completed fields, return the updated task
- DELETE /tasks/id — delete a task by id, return HTTP 204

## Storage

Use SQLite for persistence. The database file should be configurable via the DATABASE_URL environment variable.

## Requirements

- Tasks have an integer id, a title string, a boolean completed flag, and a created_at timestamp
- All endpoints return JSON
- Return HTTP 404 when a task id does not exist
- Tests must be runnable with pytest
- Single Python file or small package under src/

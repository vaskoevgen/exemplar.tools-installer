# Task Management Application Engineering Brief

## System Context
This is a demo task management web application designed as a learning project. It implements basic CRUD operations for tasks with status tracking (pending, in_progress, done). The system serves a single developer/learner with no production users or requirements.

The architecture follows a three-tier pattern: React frontend (port 5173), FastAPI Python backend (port 8000), and PostgreSQL database (port 5432), communicating via HTTP REST API. Tasks have a simple data model: id, title, description (optional), status, created_at, updated_at.

## Consequence Map
1. **Critical**: Complete task data loss - would require recreating all demo data
2. **High**: System downtime preventing development/learning progress
3. **Medium**: Data validation misalignment causing inconsistent states
4. **Low**: Concurrent access issues (single user, last write wins acceptable)

## Failure Archaeology
This is a greenfield project with no prior failure history. Building from scratch with clean separation principles.

## Dependency Landscape
- **PostgreSQL**: Authoritative data store for all task information
- **FastAPI Backend**: Sole writer to tasks table, owns data validation and business logic
- **React Frontend**: Read/write client, no direct database access
- **HTTP REST API**: Communication protocol between frontend and backend

## Boundary Conditions
- **Scope**: Demo/learning project only
- **Non-goals**: Production deployment, user authentication, audit trails, data retention
- **Constraints**: No containerization, separate processes only, no shared code between tiers
- **User Model**: Single user, concurrent access handled by last-write-wins

## Success Shape
A clean three-tier architecture where:
- All components can be run independently with clear README instructions
- CRUD operations work without page reloads
- Status transitions are enforced but flexible (any direction allowed)
- Data validation rules are aligned between frontend and backend
- Clean separation maintained with backend as authoritative source

## Done When
- All five CRUD endpoints functional (list all, get one, create, update, delete)
- React UI supports create, view, edit, delete without page reloads
- Status transitions work in any direction (pending ↔ in_progress ↔ done)
- Hard delete implementation removes rows completely from database
- Backend enforces data validation as authoritative source
- README provides clear instructions for running each component independently
- No shared code between frontend, backend, and database layers

## Trust and Authority Model
The FastAPI backend holds exclusive authority over task data domains. Task data is classified as PUBLIC tier since this is a demo project with no sensitive information. The PostgreSQL database requires basic trust verification with 1-hour soak time. No human gates are required for this demo system. The backend component owns all task-related data patterns and serves as the single source of truth for data validation and business logic.

## Component Topology
Three components form the system: a React frontend serving the user interface, a FastAPI backend providing REST API endpoints and business logic, and a PostgreSQL database storing task data. The frontend connects to the backend via HTTP REST calls on port 8000. The backend connects to the database via standard PostgreSQL protocol on port 5432. Data flows from the database through the backend to the frontend for reads, and from the frontend through the backend to the database for writes. The backend maintains exclusive write access to ensure data consistency.
# Task Management Web Application - Engineering Brief

## System Context
A simple personal task management web application serving individual users who need to create, complete, and delete tasks. The system consists of a FastAPI backend serving both a REST JSON API and a static frontend, connected to a PostgreSQL database. Users interact through a single-page vanilla JavaScript interface with no authentication required.

## Consequence Map
**CRITICAL**: Data loss (task deletion without recovery, database corruption) - destroys user productivity and trust
**HIGH**: API unavailability - blocks all user interactions, no alternative access method
**MEDIUM**: Frontend errors - degrades user experience but API remains functional
**LOW**: Performance degradation - users can still accomplish tasks with delays

## Failure Archaeology
This is a greenfield system with no prior failure history. Key risk areas identified:
- No authentication creates potential for cross-user data exposure
- No pagination may cause performance issues with large task counts
- Single process deployment creates availability bottleneck
- No backup/recovery strategy for permanent task deletion

## Dependency Landscape
**Core Dependencies**:
- Python + FastAPI framework (HTTP server, JSON serialization)
- PostgreSQL database (data persistence)
- DATABASE_URL environment variable (configuration coupling)

**System Touches**: Web browsers (via HTTP), database server (via connection pool)
**Touches System**: None - this is a leaf application

## Boundary Conditions
**Scope**: Basic CRUD operations for personal tasks, single-page frontend, JSON API
**Non-goals**: Authentication, user accounts, task sharing, mobile app, real-time updates, task categories/priorities, undo functionality, pagination
**Constraints**: Single Python process, vanilla JavaScript (no build step), PostgreSQL only

## Success Shape
- Stateless API design enabling horizontal scaling potential
- Clear separation between frontend and backend responsibilities
- Minimal deployment complexity (single process)
- Self-contained with comprehensive setup documentation
- Graceful error handling with meaningful user feedback

## Done When
- POST /tasks creates tasks accepting JSON with title field
- GET /tasks returns all tasks with optional completed filter
- PATCH /tasks/{id} marks tasks complete
- DELETE /tasks/{id} permanently removes tasks
- Database table 'tasks' with id, title, completed, created_at columns
- All responses are JSON with error responses containing 'detail' key
- README.md covers database setup, backend startup, API reference, frontend access
- System runs end-to-end from fresh checkout following README instructions

## Trust and Authority Model
No formal trust tiers defined due to system simplicity - all data treated as PUBLIC with no sensitive information handling. The web_frontend owns user interaction domain, the api_backend owns business logic domain, and the database owns persistence domain. No human gates required given non-sensitive nature of task data. Standard soak testing applies with 1-hour duration for PUBLIC tier data.

## Component Topology
Three core components: web_frontend (serves static HTML/JS), api_backend (FastAPI service handling REST endpoints), and database (PostgreSQL storage). Frontend communicates with backend via HTTP JSON API. Backend connects to database via connection pool using DATABASE_URL. Data flows: user interactions → frontend → API calls → backend → SQL queries → database, with task data flowing back through the same path.
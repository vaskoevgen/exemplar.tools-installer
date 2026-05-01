# Task Management Web Application - Engineering Brief

## System Context
A greenfield full-stack web application for personal task management. Three-tier architecture with React frontend, Node.js/Express backend, and PostgreSQL database. Single-user system designed as a learning exercise for full-stack development patterns, focusing on CRUD operations, REST API design, and database schema evolution.

**Users**: Individual developer using this as a personal task manager and learning platform
**Purpose**: Practice full-stack development skills through iterative feature development

## Consequence Map
1. **Critical**: Data loss during schema migrations - destroys learning progress and personal task data
2. **High**: API returning wrong HTTP status codes - breaks REST conventions and learning objectives
3. **High**: Frontend/backend communication failures - prevents end-to-end functionality verification
4. **Medium**: Database constraint violations - undermines schema design learning goals
5. **Low**: UI responsiveness issues - doesn't impact core learning objectives

## Failure Archaeology
This is a greenfield system with no prior failure history. Key learning risks identified:
- Schema migration complexity when adding task priorities and due dates
- HTTP status code inconsistency across different error conditions
- Frontend state management when backend becomes authoritative source
- Database constraint design for data integrity

## Dependency Landscape
**External Dependencies**:
- React (frontend framework)
- Node.js/Express (backend runtime/framework)
- PostgreSQL (database)

**Internal Components**:
- Frontend talks to Backend via REST API
- Backend talks to Database via SQL queries
- No external integrations or third-party services

## Boundary Conditions
**Scope**: CRUD operations for tasks, schema migrations, REST API patterns
**Non-goals**: Multi-user support, authentication, production deployment, advanced UI/UX
**Constraints**: Local development only, single-user, learning exercise timeline

## Success Shape
- Clean separation between frontend and backend responsibilities
- Backend as authoritative source for all data operations
- Proper HTTP semantics throughout API design
- Evolutionary database schema with migration support
- Error handling that teaches proper status code usage
- Code structure that demonstrates full-stack development patterns

## Done When
- All CRUD operations (create, read, update, delete) work end-to-end
- API returns proper HTTP status codes (400 for validation, 404 for missing resources)
- Database schema is normalized with appropriate constraints
- Schema migration successfully adds priority column with NOT NULL, default value, and index
- Task priorities and due dates functionality implemented
- Frontend communicates with backend via REST with proper error handling
- Backend maintains authoritative control over all data operations

## Trust and Authority Model
**Data Tiers**: Personal task data classified as PUBLIC (learning exercise, single-user)
**Component Authority**: Backend owns all task domain data and business logic
**Human Gates**: No automated gates required for learning environment
**Canary Soak**: Minimal soak requirements - immediate deployment acceptable for local development

## Component Topology
**Frontend**: React application handling user interface and API communication
**Backend**: Node.js/Express service providing REST API and business logic
**Database**: PostgreSQL instance storing task data with evolving schema

**Data Flow**: User actions → Frontend → REST API → Backend → SQL queries → Database
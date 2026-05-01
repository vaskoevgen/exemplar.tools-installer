```bash
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/exemplar.tools-installer (feature/howto-next-iteration)> mkdir todo-list2
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/exemplar.tools-installer (feature/howto-next-iteration)> source ../exemplar.tools/constrain/.venv/bin/activate.fish
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/exemplar.tools-installer (feature/howto-next-iteration)>  export ANTHROPIC_API_KEY=sk-***
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/exemplar.tools-installer (feature/howto-next-iteration)> clear
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/exemplar.tools-installer (feature/howto-next-iteration)> cd todo-list2
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-list2 (feature/howto-next-iteration)> constrain
Tip: Add '.constrain/' to your .gitignore to keep session data out of version control.
Prime with documents before starting? [y/N]: n
/Users/yevhenvasko/source/exemplar.tools/transmogrifier/src/transmogrifier/profiles.py:15: UserWarning: Field name "register" in "RegisterAccuracy" shadows an attribute in parent "BaseModel"
  class RegisterAccuracy(BaseModel):

I'm here to help you think through your problem systematically. Let's start with the basics:

What system or area are you working on, and what's the core issue you're trying to solve?


> A web application for managing personal tasks — create, complete, and delete tasks. I need to have frontend, backend, database

Got it - you're building a personal task management web app with the standard three-tier architecture.

Let me understand the scope better: Are you building this from scratch as a greenfield project, or are you working with an existing system that needs changes? And who is the primary user - just yourself, or do you plan to have multiple users?


> Greenfield project, just for myself as a single user


Perfect - a personal productivity tool for just you. That simplifies things significantly.

What's driving you to build this rather than using existing task management apps? Is there something specific about your workflow or requirements that existing solutions don't handle well?


> 
> It's a learning exercise to practice building full-stack apps


Ah, that changes the stakes entirely - this is about skill development, not solving a productivity problem.

What specific technologies or concepts are you hoping to learn or practice with this project? And do you have any constraints - like a timeline, specific tech stack you want to use, or particular areas where you want to challenge yourself?


> 
> React frontend, Node.js/Express backend, PostgreSQL database. No hard timeline, want to practice REST API design and database schema design.


Great tech stack for learning those concepts. Since this is about practicing REST API and database schema design, what does "done" look like for you?

Are you aiming to just get the basic CRUD operations working, or do you want to tackle more complex scenarios like task priorities, due dates, categories, or other features that would give you richer API and schema design challenges?


> 
> Start with basic CRUD, then add priorities and due dates for richer schema design practice


Perfect progression - basic CRUD first, then evolving the schema for priorities and due dates.

For your learning objectives, what would you consider concrete evidence that you've successfully practiced REST API design and database schema design? For example, would it be implementing all the standard HTTP verbs correctly, having a normalized schema, being able to handle schema migrations, or something else specific you want to demonstrate mastery of?


> 
> Proper HTTP status codes, normalized schema, and at least one schema migration when adding priorities


Excellent - those are concrete, testable learning outcomes. Since this is primarily a learning exercise with those specific technical goals, I think we have a clear picture of what you're building and why.

Just to complete the picture: besides the technology dependencies you mentioned, are there any other assumptions or constraints I should know about? For instance, are you planning to deploy this anywhere, or will local development be sufficient for your learning goals?


--- Moving to challenge phase ---


I see a few potential gaps in your acceptance criteria that could lead to passing tests for the wrong reasons:

**Testing vs. Real Learning**: Your criteria focus on "implementing" and "using proper HTTP status codes," but what happens when your API returns 200 OK for a failed database operation because you caught the exception poorly? You could technically "use proper status codes" while completely missing error handling patterns. How will you verify that your REST API actually follows REST principles beyond just returning the right numbers?

**Schema Migration Success**: You want to "successfully execute at least one schema migration," but what defines success here? If your migration runs without errors but breaks existing functionality, or if you can add the priority column but can't actually query it effectively, does that count? What's your plan for validating that the migration preserves data integrity and doesn't introduce performance issues?

Here's a critical ownership question: **What databases or storage systems does this component own?** Since you're building the full stack, your backend will own the PostgreSQL database, but which specific tables and fields will contain task data that belongs to you as the single user?


> 
> Local development only, no deployment needed for this learning exercise


Good clarification on the deployment scope. But I'm concerned about a blind spot in your "normalized schema" requirement:

**Normalization Without Context**: You want a "normalized database schema," but normalized to what degree and for what purpose? You could technically achieve 3NF by splitting tasks into multiple tables unnecessarily, passing your normalization test while creating a schema that's actually harder to work with. What specific normalization problems are you trying to solve with a single-user task system? Without multi-user data or complex relationships, you might be over-engineering just to check a box.

**API Design Validation**: Your criteria mention "REST API design practice," but REST is about much more than HTTP verbs and status codes. How will you validate that your resource design actually makes sense? For instance, is completing a task a PATCH to `/tasks/:id` with a status change, or a POST to `/tasks/:id/complete`? Both could return proper status codes, but they represent very different API design philosophies.

And here's a conflict probe: **If your frontend caches a task as "incomplete" but your backend has marked it "complete" due to a previous request, which component should be authoritative about the task's current state?** This matters for your learning because it affects how you design your API endpoints and data flow.


> 
> Backend is authoritative. Completing a task is a PATCH to /tasks/:id. Normalization just means no redundant columns — tasks in one table is fine for single-user.


Good decisions - backend authority and PATCH for updates show solid REST understanding. Your normalization approach is pragmatic for the single-user scope.

But here's where your acceptance criteria might mislead you: **Edge Case Definition**: Your criteria say "All CRUD operations work end-to-end," but what defines "work" when the correct behavior is ambiguous? For example, what should happen when you PATCH a task with an empty title, or when you DELETE a task that's already been deleted? Your tests could pass by returning 200 for both scenarios, but that might not reflect good API design learning.

**Success Metrics Gaming**: You want to "successfully execute at least one schema migration when adding task priorities," but this could be gamed by creating the most trivial migration possible - just adding a nullable priority column without any constraints, indexes, or validation. Your migration runs "successfully" but teaches you nothing about real schema evolution challenges like data type decisions, default values, or performance implications.

Storage obligation question: **Which fields in your tasks table will contain personal data, and are any of those values stored as tokens or encrypted forms rather than raw values?** Even for a single-user learning project, understanding what constitutes sensitive data in your schema affects how you think about database design patterns.


> 
> Empty title should return 400. Deleting a non-existent task should return 404. Priority column will have NOT NULL with a default value and an index.


Excellent error handling decisions and thoughtful migration planning. Those specifics show you're thinking beyond just making things "work."

Here's my final challenge on the data flow: **Stale Data Authority**: You said the backend is authoritative, but what happens when your React frontend makes a PATCH request that fails due to network issues, but the user doesn't realize it failed? Your frontend might show the task as complete while the backend still has it as incomplete. How will your API design help the frontend detect and recover from these state mismatches? This matters for your REST learning because it affects whether you need optimistic updates, response body design, or refresh strategies.

And one storage consideration: **Are any task records subject to retention requirements that would prevent deletion, or can everything be permanently deleted since this is purely personal data?** Understanding data lifecycle in your schema design - even for a simple learning project - shapes how you think about DELETE operations and whether you need soft deletes, audit trails, or true hard deletes.

Based on your responses, you've thought through the key technical decisions well. Your problem description captures a solid learning-focused project with clear scope and measurable outcomes.


--- Moving to synthesize phase ---


Generating artifacts...


--- prompt.md ---
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
**Constraints**: Local development only, single-...

--- constraints.yaml ---
constraints:
  - id: C001
    boundary: API responses
    condition: All API endpoints must return appropriate HTTP status codes (200/201 for success, 400 for validation errors, 404 for missing resources)
    violation: Incorrect status codes returned, breaking REST conventions
    severity: must
    rationale: Core learning objective for REST API design
    classification_tier: null
    affected_components: [backend]

  - id: C002
    boundary: Data operations
    condition: Backend must be authoritative source for all task data operations
    violation: Frontend directly modifies data or bypasses backend validation
    severity: must
    rationale: Enforces proper three-tier architecture patterns
    classification_tier: PUBLIC
    affected_components: [frontend, backend]

  - id: C003
    boundary: Database schema
    condition: Task table must have normalized structure with appropriate constraints
    violation: Denormalized data or missing constraints leading to data integrity issues
    severity: must
    rationale: Database design learning objective
    classification_tier: PUBLIC
    affected_components: [database]

  - id: C004
    boundary: Schema migration
    condition: Priority column addition must include NOT NULL constraint, default value, and index
    violation: Migration fails or creates inconsistent schema state
    severity: must
    rationale: Schema evolution learning objective
    classification_tier: PUBLIC
    affected_components: [database]

  - id: C005
    boundary: API communication
    condition: All frontend-backend communication must use REST API endpoints
    violation: Direct database access or non-REST communication patterns
    severity: must
    rationale: Proper separation of concerns and API design learning
    classification_tier: PUBLIC
    affected_components: [frontend, backend]

  - id: C006
    boundary: Error handling
    condition: Frontend must handle all API error responses gracefully
    violation: Unhandled errors o...

--- trust_policy.yaml ---
version: "1.0"
generated_by: constrain
session_id: learning_exercise_001
system: Task Management Web Application

trust:
  floor: 0.90
  authority_override_floor: 0.90
  decay_lambda: 0.01
  taint_lock_tiers: []
  conflict_trust_delta_threshold: 0.10

classifications:
  - field_pattern: "task.*"
    tier: PUBLIC
    authoritative_component: "backend"
    canary_eligible: true
    canary_pattern: "task_id"
    rationale: "Personal learning exercise with single user, no sensitive data"

  - field_pattern: "priority"
    tier: PUBLIC
    authoritative_component: "backend"
    canary_eligible: true
    canary_pattern: "priority_level"
    rationale: "Task priority metadata for schema evolution learning"

  - field_pattern: "due_date"
    tier: PUBLIC
    authoritative_component: "backend"
    canary_eligible: true
    canary_pattern: "due_timestamp"
    rationale: "Task scheduling metadata for advanced feature learning"

soak:
  base_durations:
    PUBLIC: 5m
  target_requests: 10

authority_map:
  - component: "backend"
    domains: ["task.*", "priority.*", "due_date.*"]
    rationale: "Backend is authoritative for all business logic and data validation"

human_gates:
  always: []
  on_low_trust_authoritative: false
  on_unresolvable_conflict: false

--- component_map.yaml ---
version: "1.0"
generated_by: constrain
session_id: learning_exercise_001

components:
  - name: "frontend"
    description: "React application providing user interface for task management"
    type: service
    port: 3000
    protocol: http
    data_access:
      reads: [PUBLIC]
      writes: []
      rationale: "Frontend reads data via API calls but does not directly write to storage"
    authority:
      domains: []
      rationale: null
    dependencies: ["backend"]
    constraints: ["C002", "C005", "C006", "C007"]

  - name: "backend"
    description: "Node.js/Express REST API providing business logic and data operations"
    type: service
    port: 3001
    protocol: http
    data_access:
      reads: [PUBLIC]
      writes: [PUBLIC]
      rationale: "Backend handles all data operations and serves as API layer"
    authority:
      domains: ["task.*", "priority.*", "due_date.*"]
      rationale: "Authoritative source for all task-related business logic and validation"
    dependencies: ["database"]
    constraints: ["C001", "C002", "C005", "C007"]

  - name: "database"
    description: "PostgreSQL database storing task data with evolving schema"
    type: service
    port: 5432
    protocol: tcp
    data_access:
      reads: [PUBLIC]
      writes: [PUBLIC]
      rationale: "Persistent storage for all task data with schema migration support"
    authority:
      domains: []
      rationale: null
    dependencies: []
    constraints: ["C003", "C004", "C007"]

edges:
  - from: "frontend"
    to: "backend"
    protocol: http
    description: "REST API calls for task CRUD operations"

  - from: "backend"
    to: "database"
    protocol: tcp
    description: "SQL queries for data persistence and retrieval"

--- schema_hints.yaml ---
version: "1.0"
generated_by: constrain
session_id: learning_exercise_001

storage_backends:
  - owner_component: "database"
    type: postgres
    description: "Primary storage for task data with schema evolution support"

field_hints:
  - backend_owner: "database"
    field_description: "Task identifier for unique record identification"
    likely_classification: PUBLIC
    likely_annotations: [immutable]
    rationale: "Primary key field should be immutable once created"

  - backend_owner: "database"
    field_description: "Task title or description text"
    likely_classification: PUBLIC
    likely_annotations: []
    rationale: "Basic task content for personal use, no sensitive data"

  - backend_owner: "database"
    field_description: "Task completion status boolean"
    likely_classification: PUBLIC
    likely_annotations: []
    rationale: "Simple status tracking, no sensitivity"

  - backend_owner: "database"
    field_description: "Task priority level for advanced schema practice"
    likely_classification: PUBLIC
    likely_annotations: []
    rationale: "Priority metadata added during schema migration learning exercise"

  - backend_owner: "database"
    field_description: "Task due date for advanced functionality"
    likely_classification: PUBLIC
    likely_annotations: []
    rationale: "Scheduling feature for expanded learning objectives"

  - backend_owner: "database"
    field_description: "Record creation timestamp"
    likely_classification: PUBLIC
    likely_annotations: [immutable, audit_field]
    rationale: "Audit trail for learning proper timestamp handling"

  - backend_owner: "database"
    field_description: "Record last updated timestamp"
    likely_classification: PUBLIC
    likely_annotations: [audit_field]
    rationale: "Audit trail for tracking modifications"

Review the artifacts above. Enter feedback to revise, or press Enter/Ctrl+D to accept.

Feedback> 
Artifacts written:
  /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/prompt.md
  /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/constraints.yaml
  /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/trust_policy.yaml
  /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/component_map.yaml
  /Users/yevhenvasko/source/exemplar.tools-installer/todo-list2/schema_hints.yaml
```
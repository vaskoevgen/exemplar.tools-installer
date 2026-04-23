# URL Shortener Web Service

## System Context

You are implementing a URL shortener web service that accepts long URLs from users and returns short links. The system consists of three main components: a FastAPI REST backend, a single-page HTML + vanilla JavaScript frontend, and a PostgreSQL database. Users paste long URLs into the web interface and receive 6-character alphanumeric short codes. When someone visits the short link, they are redirected to the original URL and a hit counter increments.

This is a v1 internal system with no authentication, serving internal developers and users within the organization. The system runs as a single deployable unit where the API serves both REST endpoints and static frontend files on port 8000.

## Consequence Map

1. **Critical**: Database corruption or data loss could permanently break all existing short links, causing widespread link rot across internal systems and communications
2. **High**: Race conditions in hit counting could lead to inaccurate analytics and potential database deadlocks under concurrent load
3. **Medium**: Failed redirects while hit counts succeed create misleading usage metrics and poor user experience
4. **Low**: Duplicate URL handling inconsistencies could waste storage but don't break core functionality

## Failure Archaeology

The problem model identifies two specific failure modes:
- **Hit count race conditions**: Multiple concurrent accesses to the same short code could create database race conditions when incrementing hit counts
- **Partial failure states**: Hit count increment may succeed while redirect fails (or vice versa), creating inconsistent state between analytics and user experience

No previous attempts or solutions have been tried yet - this is greenfield development.

## Dependency Landscape

**Direct Dependencies**:
- PostgreSQL database (stores links table with id, short_code, original_url, created_at, hit_count)
- Python 3.12 runtime
- FastAPI web framework
- psycopg2 PostgreSQL adapter
- pytest testing framework

**What This Touches**:
- Internal users who create and share short links
- External websites that receive redirect traffic
- Internal systems that may embed generated short links

**What Touches This**:
- User browsers accessing the web UI and clicking short links
- Internal tools that may programmatically create short links via API

## Boundary Conditions

**In Scope**:
- Single deployable unit (API serves frontend static files)
- Raw SQL only (no ORM)
- Real database for all tests (no mocking)
- Three API endpoints: POST /shorten, GET /{code}, GET /links
- Basic web UI with form and links table

**Out of Scope (v1)**:
- User authentication or authorization
- URL expiration or TTL
- Custom aliases or vanity URLs
- Multiple deployment instances
- Public internet traffic
- Advanced analytics beyond hit counts

**Constraints**:
- Must use pytest for all testing
- Single instance deployment only
- No external authentication providers

## Success Shape

A good solution will:
- Handle concurrent access safely without race conditions
- Maintain data consistency between hit counts and redirects
- Generate truly random 6-character alphanumeric codes
- Return existing codes for duplicate URLs efficiently
- Provide fast redirect responses (< 100ms typical)
- Gracefully handle database connection issues
- Present a clean, functional web interface
- Support thousands of links without performance degradation

## Done When

- [ ] POST /shorten endpoint accepts JSON with `url` field and returns short_code
- [ ] GET /{code} endpoint redirects to original URL and increments hit_count atomically
- [ ] GET /links endpoint returns all links with metadata including hit counts
- [ ] Database schema created with proper indexes on short_code
- [ ] Frontend form successfully creates short links and displays them
- [ ] Frontend table shows all existing links with click counts
- [ ] Duplicate URL submission returns existing short_code consistently
- [ ] All database operations use raw SQL (no ORM)
- [ ] Test suite covers all endpoints using pytest with real test database
- [ ] Hit count increments are atomic and race-condition safe
- [ ] System handles at least 100 concurrent redirects without data corruption

## Trust and Authority Model

**Data Tiers**: 
- PUBLIC: Short codes, original URLs, hit counts, creation timestamps (all link data is considered public within the organization)

**Component Authority**:
- url_shortener_api: Owns all link data domains (URL mapping, analytics, code generation)

**Human Gates**: 
- No human approval gates required - all data is public tier
- No low-trust authority scenarios apply

**Canary Soak**: 
- PUBLIC data requires 1-hour soak with 1000+ test requests before promotion
- All link operations are canary-eligible for gradual rollout testing

## Component Topology

**Components**:
- **url_shortener_api**: FastAPI service handling REST endpoints and serving static files on port 8000
- **frontend_ui**: Single-page HTML/JavaScript interface served by the API, provides form for URL submission and table view of existing links
- **postgres_db**: PostgreSQL database storing the links table with all URL mappings and metadata

**Data Flow**:
- frontend_ui ↔ url_shortener_api: HTTP requests for link creation, listing, and static file serving
- url_shortener_api ↔ postgres_db: SQL queries for link CRUD operations and hit count updates
- External browsers → url_shortener_api: Direct HTTP requests to short link endpoints for redirects

The API component serves as the central hub, handling all business logic, data persistence, and frontend delivery in a single deployable unit.
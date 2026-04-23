# === Main (root) v1 ===
# URL shortener web service — a single deployable Python 3.12 / FastAPI app. Users submit a long URL via POST /shorten and receive a short redirect link. GET /{code} performs a 307 redirect and atomically increments hit_count. GET /links returns all stored links. GET / serves the static HTML frontend. Database is PostgreSQL via psycopg2-binary with raw parameterised SQL. Composed of four modules: config.py (env config), db.py (connection + query helpers), shortener.py (business logic), main.py (FastAPI routes and lifecycle).

# Module invariants:
#   - All SQL queries use parameterised placeholders ($1, %s) — never string interpolation or f-strings.
#   - Short codes are exactly 6 URL-safe characters matching the regex [A-Za-z0-9_-]{6}.
#   - The original_url column has a UNIQUE constraint; submitting the same URL always returns the existing code (idempotent).
#   - The short_code column has a UNIQUE constraint; collisions are retried up to 5 times before raising CodeCollisionError.
#   - hit_count is incremented atomically via UPDATE ... SET hit_count = hit_count + 1 RETURNING original_url.
#   - DATABASE_URL must be a valid PostgreSQL connection string or the app refuses to start.
#   - Route definition order in main.py: GET /, GET /links, GET /{code}, POST /shorten — to prevent path parameter from capturing literal paths.
#   - No ORM or SQLAlchemy — only raw SQL via psycopg2-binary.
#   - Each source file is under 200 lines.

DatabaseUrl = primitive  # PostgreSQL connection string in the form postgresql://user:pass@host:port/dbname.

ShortCode = primitive  # A 6-character URL-safe alphanumeric code uniquely identifying a shortened link.

OriginalUrl = primitive  # A user-submitted URL to be shortened. Must be a valid HTTP or HTTPS URL.

class AppConfig:
    """Application-level configuration read from environment variables."""
    database_url: DatabaseUrl                # required, PostgreSQL connection string from DATABASE_URL env var.
    base_url: String                         # required, Base URL prefix used to construct short_url values in responses.
    max_code_retries: Int                    # required, Maximum number of attempts to generate a unique short code before raising an error.

class ShortenRequest:
    """Request body for POST /shorten containing the long URL to shorten."""
    url: Url                                 # required, The original long URL to be shortened.

class ShortenResponse:
    """Response body for POST /shorten returning the generated short URL and its code."""
    short_url: Url                           # required, Fully-qualified short redirect URL (e.g. http://localhost:8000/abc123).
    code: ShortCode                          # required, The 6-character short code portion of the URL.

class LinkListItem:
    """Public-facing link summary returned in the GET /links JSON array (excludes internal id)."""
    code: ShortCode                          # required, The 6-character short code.
    original_url: Url                        # required, The original long URL.
    created_at: DateTime                     # required, Timestamp when the link was created.
    hit_count: Int                           # required, Cumulative redirect count.

class ErrorResponse:
    """Standard JSON error body returned for 4xx/5xx responses."""
    detail: String                           # required, Human-readable error message.

class CodeCollisionError:
    """Raised when generate_code() fails to produce a unique short code after max_retries attempts. Mapped to HTTP 503 by the exception handler in main.py."""
    attempts: int                            # required, range(1..5), Number of code generation attempts made before giving up.
    message: str                             # required, Descriptive error message.

class HttpMethod(Enum):
    """HTTP methods used by the API routes."""
    GET = "GET"
    POST = "POST"

RowDict = primitive  # A dictionary representing a single database row returned by RealDictCursor. Keys are column names, values are Python-typed column values.

String = primitive  # UTF-8 string value.

Int = primitive  # Signed integer (32-bit or platform default).

DateTime = primitive  # ISO-8601 timestamp with timezone (maps to Python datetime and PostgreSQL TIMESTAMPTZ).

Url = primitive  # A valid absolute HTTP or HTTPS URL represented as a string.

def config.get_config() -> AppConfig:
    """
    Returns the application configuration singleton. Reads DATABASE_URL from environment on first call, caches the result for subsequent calls. Raises RuntimeError if DATABASE_URL is not set or is empty.

    Preconditions:
      - Environment variable DATABASE_URL must be set and non-empty.

    Postconditions:
      - Returned AppConfig.database_url matches the value of os.environ['DATABASE_URL'].
      - Subsequent calls return the same cached AppConfig instance (singleton).

    Errors:
      - missing_database_url (RuntimeError): DATABASE_URL environment variable is not set or is empty string.
          message: DATABASE_URL environment variable is required but not set.

    Side effects: none
    Idempotent: yes
    """
    ...

def db.get_conn() -> any:
    """
    Returns a psycopg2 connection to PostgreSQL. Lazily initialises the connection on first call using config.get_config().database_url. Returns the existing connection on subsequent calls. Connection has autocommit=True.

    Preconditions:
      - config.get_config() must succeed (DATABASE_URL set).
      - PostgreSQL server must be reachable at the configured URL.

    Postconditions:
      - Returned connection is open and usable for queries.
      - Connection has autocommit=True.

    Errors:
      - connection_failed (psycopg2.OperationalError): PostgreSQL is unreachable or credentials are invalid.
          message: Could not connect to PostgreSQL at the configured DATABASE_URL.
      - config_missing (RuntimeError): DATABASE_URL not set, propagated from config.get_config().
          message: DATABASE_URL environment variable is required but not set.

    Side effects: none
    Idempotent: yes
    """
    ...

def db.execute(
    query: str,
    params: any = (),
) -> list:
    """
    Executes a parameterised SQL query and returns all result rows as a list of dicts (via RealDictCursor). Returns an empty list for statements with no result set (INSERT without RETURNING, etc.).

    Preconditions:
      - db.get_conn() has been called or will be called internally.
      - query uses %s placeholders — no string interpolation.

    Postconditions:
      - All returned dicts have keys matching the SELECT column names.
      - For non-SELECT statements, returns empty list.

    Errors:
      - query_error (psycopg2.Error): SQL syntax error or constraint violation.
          message: Database query execution failed.
      - connection_lost (psycopg2.OperationalError): PostgreSQL connection was dropped.
          message: Database connection lost during query execution.

    Side effects: none
    Idempotent: no
    """
    ...

def db.execute_one(
    query: str,
    params: any = (),
) -> any:
    """
    Executes a parameterised SQL query and returns the first row as a dict, or None if no rows are returned. Convenience wrapper around execute().

    Preconditions:
      - query uses %s placeholders — no string interpolation.

    Postconditions:
      - Returns the first row as a dict if result set is non-empty, else None.
      - Does not consume or return subsequent rows.

    Errors:
      - query_error (psycopg2.Error): SQL syntax error or constraint violation.
          message: Database query execution failed.
      - connection_lost (psycopg2.OperationalError): PostgreSQL connection was dropped.
          message: Database connection lost during query execution.

    Side effects: none
    Idempotent: no
    """
    ...

def db.close_conn() -> None:
    """
    Closes the cached PostgreSQL connection if one is open. Safe to call multiple times. Used during application shutdown.

    Postconditions:
      - Any cached connection is closed and the module-level reference is reset to None.
      - Subsequent calls to get_conn() will open a fresh connection.

    Side effects: none
    Idempotent: yes
    """
    ...

def shortener.generate_code() -> ShortCode:
    """
    Generates a 6-character URL-safe short code using secrets.token_urlsafe(4)[:6]. This is a pure function with no side effects — collision detection is handled by the caller (shorten_url).

    Postconditions:
      - Returned string is exactly 6 characters.
      - Returned string matches [A-Za-z0-9_-]{6}.

    Side effects: none
    Idempotent: no
    """
    ...

def shortener.shorten_url(
    original_url: OriginalUrl, # regex(^https?://[^\s]{3,2048}$)
) -> ShortenResponse:
    """
    Shortens a URL. If the original_url already exists in the links table, returns the existing code (idempotent). Otherwise generates a new short code, inserts the row, and returns the ShortenResponse. Retries up to 5 times on short_code collision (UNIQUE constraint violation).

    Preconditions:
      - Database connection is available.
      - The links table exists with the expected schema.

    Postconditions:
      - A row with the given original_url exists in the links table.
      - Returned ShortenResponse.code corresponds to the row's short_code.
      - Returned ShortenResponse.short_url is http://localhost:8000/{code}.
      - If the URL already existed, no new row was inserted and the existing code is returned.

    Errors:
      - code_collision_exhausted (CodeCollisionError): All 5 retry attempts produced short codes that collide with existing codes.
          attempts: 5
          message: Failed to generate a unique short code after 5 attempts.
      - database_error (psycopg2.Error): Unexpected database error during INSERT or SELECT.
          message: Database error during URL shortening.

    Side effects: none
    Idempotent: yes
    """
    ...

def shortener.resolve_and_track(
    code: ShortCode,           # regex(^[A-Za-z0-9_-]{6}$), length(6..6)
) -> any:
    """
    Resolves a short code to its original URL and atomically increments hit_count. Uses a single UPDATE links SET hit_count = hit_count + 1 WHERE short_code = %s RETURNING original_url query for atomicity.

    Preconditions:
      - Database connection is available.
      - The links table exists with the expected schema.

    Postconditions:
      - If a row with matching short_code exists: hit_count is incremented by exactly 1, and original_url is returned.
      - If no row matches: None is returned and no rows are modified.

    Errors:
      - database_error (psycopg2.Error): Unexpected database error during UPDATE.
          message: Database error during code resolution.

    Side effects: none
    Idempotent: no
    """
    ...

def shortener.list_links() -> list:
    """
    Returns all link records from the links table, ordered by created_at descending (newest first). Maps each row dict to a LinkListItem.

    Preconditions:
      - Database connection is available.
      - The links table exists with the expected schema.

    Postconditions:
      - Returned list contains one LinkListItem per row in the links table.
      - List is ordered by created_at descending.
      - Each LinkListItem.hit_count reflects the current database value.

    Errors:
      - database_error (psycopg2.Error): Unexpected database error during SELECT.
          message: Database error during link listing.

    Side effects: none
    Idempotent: yes
    """
    ...

async def main.post_shorten(
    body: ShortenRequest,
) -> ShortenResponse:
    """
    FastAPI route handler: POST /shorten. Accepts a JSON body with a URL, delegates to shortener.shorten_url(), and returns a ShortenResponse. CodeCollisionError is caught by a global exception handler and returned as a 503 ErrorResponse.

    Preconditions:
      - Request body is valid JSON conforming to ShortenRequest schema.
      - Database is reachable.

    Postconditions:
      - Response status is 200.
      - Response body is a valid ShortenResponse.
      - A link row exists in the database for the given URL.

    Errors:
      - validation_error (ErrorResponse): Request body fails Pydantic validation (missing url, invalid format).
          http_status: 422
          detail: Validation error for request body.
      - code_collision (ErrorResponse): shortener.shorten_url() raises CodeCollisionError after 5 retry attempts.
          http_status: 503
          detail: Failed to generate a unique short code. Try again later.

    Side effects: none
    Idempotent: yes
    """
    ...

async def main.get_redirect(
    code: ShortCode,           # regex(^[A-Za-z0-9_-]{6}$), length(6..6)
) -> any:
    """
    FastAPI route handler: GET /{code}. Resolves the short code via shortener.resolve_and_track() and returns an HTTP 307 redirect to the original URL. Returns 404 if the code does not exist.

    Preconditions:
      - Database is reachable.

    Postconditions:
      - If code exists: HTTP 307 redirect to original_url. hit_count incremented by 1.
      - If code does not exist: HTTP 404 with ErrorResponse body.

    Errors:
      - code_not_found (ErrorResponse): No link exists with the given short_code.
          http_status: 404
          detail: Short link not found.

    Side effects: none
    Idempotent: no
    """
    ...

async def main.get_links() -> list:
    """
    FastAPI route handler: GET /links. Returns a JSON array of all link records via shortener.list_links().

    Preconditions:
      - Database is reachable.

    Postconditions:
      - Response status is 200.
      - Response body is a JSON array of LinkListItem objects.
      - Array is ordered by created_at descending.

    Errors:
      - database_error (ErrorResponse): Database unreachable or query failure.
          http_status: 500
          detail: Internal server error.

    Side effects: none
    Idempotent: yes
    """
    ...

async def main.get_index() -> any:
    """
    FastAPI route handler: GET /. Serves static/index.html as a FileResponse with content-type text/html.

    Preconditions:
      - File static/index.html exists on disk relative to the application root.

    Postconditions:
      - Response status is 200.
      - Response content-type is text/html.
      - Response body is the contents of static/index.html.

    Errors:
      - file_not_found (ErrorResponse): static/index.html does not exist on disk.
          http_status: 404
          detail: Index file not found.

    Side effects: none
    Idempotent: yes
    """
    ...

async def main.startup_event() -> None:
    """
    FastAPI startup lifecycle event handler. Verifies the database connection is viable by calling db.get_conn(). Logs a message on success. If the connection fails, the error propagates and prevents uvicorn from accepting requests.

    Preconditions:
      - DATABASE_URL environment variable is set.
      - PostgreSQL server is reachable.

    Postconditions:
      - A database connection has been established and cached in db module.
      - Application is ready to accept HTTP requests.

    Errors:
      - db_unreachable (psycopg2.OperationalError): PostgreSQL is not reachable at startup.
          message: Cannot connect to PostgreSQL. Application startup aborted.
      - config_missing (RuntimeError): DATABASE_URL not set.
          message: DATABASE_URL environment variable is required but not set.

    Side effects: none
    Idempotent: yes
    """
    ...

async def main.shutdown_event() -> None:
    """
    FastAPI shutdown lifecycle event handler. Calls db.close_conn() to cleanly close the PostgreSQL connection.

    Postconditions:
      - Database connection is closed.
      - Module-level connection reference in db.py is reset to None.

    Side effects: none
    Idempotent: yes
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['AppConfig', 'ShortenRequest', 'ShortenResponse', 'LinkListItem', 'ErrorResponse', 'CodeCollisionError', 'HttpMethod']

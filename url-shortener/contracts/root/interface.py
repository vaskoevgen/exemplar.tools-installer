# === Main (root) v1 ===
# URL shortener web service — a single deployable Python app composed of 4 modules (config.py, db.py, shortener.py, main.py). Users POST a long URL to receive a short redirect code; GET /{code} performs an atomic hit-count increment and 307 redirect. All data persisted in PostgreSQL via raw parameterised SQL (psycopg2-binary, no ORM). Static frontend served from /static, root serves index.html.

# Module invariants:
#   - The links table has a UNIQUE constraint on short_code — no two rows share the same short_code.
#   - The links table has a UNIQUE constraint on original_url — each URL is shortened at most once (idempotent).
#   - hit_count is non-negative and monotonically non-decreasing for any given link row.
#   - short_code is always exactly 6 characters, drawn from the URL-safe base64 alphabet ([A-Za-z0-9_-]).
#   - All SQL queries use parameterised placeholders (%s) — no string interpolation.
#   - Route declaration order in main.py ensures /links and / are matched before /{code}.
#   - POST /shorten is idempotent: repeated calls with the same URL return the same short_code.
#   - DATABASE_URL must be set as an environment variable before any DB operation.

DatabaseUrl = primitive  # PostgreSQL connection string in the form postgresql://user:pass@host:port/dbname.

ShortCode = primitive  # A 6-character URL-safe string uniquely identifying a shortened link.

OriginalUrl = primitive  # A validated URL string representing the long URL to be shortened.

HitCount = primitive  # Non-negative integer tracking the number of times a short link has been accessed.

class ShortenRequest:
    """Request body for POST /shorten containing the original long URL to shorten."""
    url: Url                                 # required, length(min=1), The original long URL the user wants shortened.

class ShortenResponse:
    """Response body for POST /shorten containing the generated short URL and its code."""
    short_url: Url                           # required, Fully qualified short URL (e.g. http://localhost:8000/abc123).
    code: ShortCode                          # required, The 6-character short code portion of the URL.

class LinkRecord:
    """A single shortened-link record as stored in the database and returned by GET /links."""
    id: Int                                  # required, Auto-incrementing primary key (SERIAL).
    short_code: ShortCode                    # required, length(min=6,max=6), Unique 6-character code for the link.
    original_url: Url                        # required, The original long URL that this code redirects to.
    created_at: DateTime                     # required, Timestamp (with timezone) when the link was created.
    hit_count: Int                           # required, range(min=0), Number of times the short link has been visited.

class LinkListItem:
    """Public projection of a link record returned in the GET /links JSON array (excludes internal id)."""
    code: ShortCode                          # required, The 6-character short code.
    original_url: Url                        # required, The original long URL.
    created_at: DateTime                     # required, When the link was created.
    hit_count: Int                           # required, range(min=0), Total redirect count for this link.

LinkList = list[LinkListItem]
# JSON array of all shortened links returned by GET /links.

class ErrorDetail:
    """Standard error response body returned for 404 and other error cases."""
    detail: String                           # required, Human-readable error message.

class MaxRetriesExhaustedCode(Enum):
    """Enum for short-code generation failure modes when collision retries are exhausted."""
    COLLISION_LIMIT_REACHED = "COLLISION_LIMIT_REACHED"

class AppConfig:
    """Application configuration read from environment variables, shared between config, db, and main modules."""
    database_url: DatabaseUrl                # required, regex(^postgresql://), PostgreSQL connection string from DATABASE_URL env var.
    base_url: Url = http://localhost:8000    # optional, Base URL prefix used to construct full short_url values in responses.

String = primitive  # UTF-8 string value.

Int = primitive  # Integer value (32-bit or platform default).

DateTime = primitive  # ISO-8601 timestamp with timezone (maps to Python datetime and PostgreSQL TIMESTAMPTZ).

Url = primitive  # A valid absolute HTTP or HTTPS URL represented as a string.

def get_database_url() -> DatabaseUrl:
    """
    Reads DATABASE_URL from os.environ and returns it. Raises if the variable is not set. Located in config.py.

    Preconditions:
      - Environment variable DATABASE_URL is set and non-empty.

    Postconditions:
      - Returned string starts with 'postgresql://'.

    Errors:
      - missing_env_var (KeyError): DATABASE_URL is not set in os.environ
          detail: DATABASE_URL environment variable is not set.

    Side effects: none
    Idempotent: yes
    """
    ...

def get_conn() -> any:
    """
    Returns a new psycopg2 connection to PostgreSQL using the DATABASE_URL from config. Connection uses RealDictCursor as the default cursor factory. Located in db.py. Caller is responsible for closing the connection.

    Preconditions:
      - DATABASE_URL environment variable is set.
      - PostgreSQL server is reachable at the configured address.

    Postconditions:
      - Returned connection is open and uses RealDictCursor as default cursor factory.
      - Connection autocommit is False (psycopg2 default).

    Errors:
      - connection_failed (psycopg2.OperationalError): PostgreSQL server is unreachable or credentials are invalid.
          detail: Could not connect to PostgreSQL.
      - missing_database_url (KeyError): DATABASE_URL is not set in environment.
          detail: DATABASE_URL environment variable is not set.

    Side effects: none
    Idempotent: yes
    """
    ...

def generate_code() -> ShortCode:
    """
    Generates a 6-character URL-safe short code using secrets.token_urlsafe(4)[:6]. Located in shortener.py. Pure function (no DB interaction); collision detection is handled by the caller (shorten_url).

    Postconditions:
      - Returned code is exactly 6 characters.
      - Returned code contains only characters from [A-Za-z0-9_-].

    Side effects: none
    Idempotent: no
    """
    ...

def shorten_url(
    original_url: str,         # regex(^https?://\S+$)
    base_url: str,             # regex(^https?://\S+$)
) -> ShortenResponse:
    """
    Shortens a URL: if the URL already exists in the links table, returns the existing record's code. Otherwise generates a new short code, inserts it, and returns the result. Retries up to 5 times on short_code collision (UniqueViolation on short_code). Located in shortener.py.

    Preconditions:
      - Database is reachable and links table exists.
      - original_url is a valid http or https URL.

    Postconditions:
      - A row with the given original_url exists in the links table.
      - Returned ShortenResponse.code is the short_code associated with original_url.
      - Returned ShortenResponse.short_url equals base_url + '/' + code.
      - If the URL already existed, no new row was inserted (idempotent).

    Errors:
      - max_retries_exhausted (RuntimeError): 5 consecutive short_code collisions during INSERT (all generated codes already exist for different URLs).
          detail: Could not generate a unique short code after 5 attempts.
      - database_error (psycopg2.Error): PostgreSQL connection or query fails for reasons other than short_code collision.
          detail: Database error during shorten operation.

    Side effects: none
    Idempotent: yes
    """
    ...

def get_link(
    code: str,                 # length(6..6), regex(^[A-Za-z0-9_-]{6}$)
) -> str | None:
    """
    Resolves a short code to its original URL. Atomically increments hit_count via UPDATE links SET hit_count = hit_count + 1 WHERE short_code = %s RETURNING original_url. Returns the URL string or None if the code does not exist. Located in shortener.py.

    Preconditions:
      - Database is reachable and links table exists.

    Postconditions:
      - If a row with matching short_code exists: hit_count has been incremented by 1, and the original_url is returned.
      - If no row matches: None is returned and no rows are modified.

    Errors:
      - database_error (psycopg2.Error): PostgreSQL connection or query fails.
          detail: Database error during link lookup.

    Side effects: none
    Idempotent: no
    """
    ...

def list_links() -> LinkList:
    """
    Returns all rows from the links table as a list of LinkListItem, ordered by created_at descending. Located in shortener.py.

    Preconditions:
      - Database is reachable and links table exists.

    Postconditions:
      - Returned list contains one LinkListItem per row in the links table.
      - Items are ordered by created_at descending (newest first).

    Errors:
      - database_error (psycopg2.Error): PostgreSQL connection or query fails.
          detail: Database error during link listing.

    Side effects: none
    Idempotent: yes
    """
    ...

def route_index() -> any:
    """
    GET / — serves static/index.html via FileResponse. Located in main.py.

    Preconditions:
      - File static/index.html exists on disk at the expected path.

    Postconditions:
      - Response Content-Type is text/html.
      - Response status is 200.

    Errors:
      - file_not_found (HTTPException): static/index.html does not exist at the expected path.
          status_code: 500
          detail: Index file not found.

    Side effects: none
    Idempotent: yes
    """
    ...

def route_shorten(
    body: ShortenRequest,
) -> ShortenResponse:
    """
    POST /shorten — accepts ShortenRequest JSON body, delegates to shortener.shorten_url(), returns ShortenResponse. Located in main.py.

    Preconditions:
      - Request body is valid JSON conforming to ShortenRequest schema.
      - Database is reachable.

    Postconditions:
      - Response status is 200.
      - Response body conforms to ShortenResponse schema.
      - A link record for the given URL exists in the database.

    Errors:
      - validation_error (HTTPException): Request body fails ShortenRequest validation (missing url, invalid format).
          status_code: 422
          detail: Validation error.
      - max_retries_exhausted (HTTPException): shortener.shorten_url raises RuntimeError due to code collision exhaustion.
          status_code: 500
          detail: Could not generate a unique short code after 5 attempts.
      - database_error (HTTPException): Database is unreachable or query fails.
          status_code: 500
          detail: Internal server error.

    Side effects: none
    Idempotent: yes
    """
    ...

def route_redirect(
    code: str,                 # length(6..6), regex(^[A-Za-z0-9_-]{6}$)
) -> any:
    """
    GET /{code} — resolves short code via shortener.get_link(), returns HTTP 307 redirect or 404. Located in main.py.

    Preconditions:
      - Database is reachable.

    Postconditions:
      - If code exists: response is HTTP 307 with Location header set to the original URL, and hit_count for the code has been incremented by 1.
      - If code does not exist: response is HTTP 404 with ErrorDetail body.

    Errors:
      - code_not_found (HTTPException): No link record exists with the given short_code.
          status_code: 404
          detail: Short link not found.
      - database_error (HTTPException): Database is unreachable or query fails.
          status_code: 500
          detail: Internal server error.

    Side effects: none
    Idempotent: no
    """
    ...

def route_list_links() -> LinkList:
    """
    GET /links — returns JSON array of all links via shortener.list_links(). Located in main.py.

    Preconditions:
      - Database is reachable.

    Postconditions:
      - Response status is 200.
      - Response body is a JSON array conforming to list[LinkListItem] schema.

    Errors:
      - database_error (HTTPException): Database is unreachable or query fails.
          status_code: 500
          detail: Internal server error.

    Side effects: none
    Idempotent: yes
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['ShortenRequest', 'ShortenResponse', 'LinkRecord', 'LinkListItem', 'LinkList', 'ErrorDetail', 'MaxRetriesExhaustedCode', 'AppConfig', 'get_database_url', 'get_conn', 'generate_code', 'shorten_url', 'get_link', 'list_links', 'route_index', 'HTTPException', 'route_shorten', 'route_redirect', 'route_list_links']

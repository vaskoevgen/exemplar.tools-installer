"""Custom exception classes for the database component."""


class ConnectionError(Exception):
    """PostgreSQL server is not running or not reachable."""
    pass


class AuthenticationError(Exception):
    """Credentials in DATABASE_URL are invalid."""
    pass


class DatabaseNotFoundError(Exception):
    """The database name in DATABASE_URL does not exist."""
    pass


class SQLSyntaxError(Exception):
    """The init.sql script contains a syntax error."""
    pass

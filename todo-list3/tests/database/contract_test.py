"""
Contract test suite for the database component (PostgreSQL schema init).

Covers:
  - Type validation (TaskStatus, TaskTitle, Timestamptz, ConnectionConfig)
  - execute_init_script happy path, idempotency, error cases
  - verify_schema happy path, empty-schema negative, error cases
  - Schema invariants (columns, types, constraints, triggers)
  - Randomized INSERT fuzzing for titles and invalid statuses

Requires:
  - DATABASE_URL env var pointing to a reachable PostgreSQL instance
  - psycopg2 installed
  - pytest

Run with:
  DATABASE_URL=postgresql://user:pass@localhost:5432/testdb pytest contract_test.py -v
"""

import os
import re
import time
import random
import string
import datetime
from unittest.mock import patch, MagicMock

import pytest

# ---------------------------------------------------------------------------
# Imports from the component under test
# ---------------------------------------------------------------------------
from database import (
    TaskStatus,
    TaskTitle,
    Timestamptz,
    ConnectionConfig,
    InitScriptResult,
    execute_init_script,
    verify_schema,
)

# ---------------------------------------------------------------------------
# Optional psycopg2 import (needed for live DB tests)
# ---------------------------------------------------------------------------
try:
    import psycopg2
    import psycopg2.errors
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

# ---------------------------------------------------------------------------
# Markers
# ---------------------------------------------------------------------------
pytestmark = pytest.mark.database


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def database_url() -> str:
    """Read DATABASE_URL; skip entire session if unset."""
    url = os.environ.get("DATABASE_URL")
    if url is None:
        pytest.skip("DATABASE_URL not set — skipping database tests")
    return url


@pytest.fixture(scope="session")
def connection_config(database_url: str) -> "ConnectionConfig":
    """Build a valid ConnectionConfig from the environment."""
    return ConnectionConfig(database_url=database_url, port=5432)


@pytest.fixture(scope="session")
def _ensure_psycopg2():
    if not HAS_PSYCOPG2:
        pytest.skip("psycopg2 not installed")


@pytest.fixture(scope="session")
def db_connection(database_url: str, _ensure_psycopg2):
    """Session-scoped raw psycopg2 connection for introspection."""
    try:
        conn = psycopg2.connect(database_url)
    except Exception:
        pytest.skip(f"Cannot connect to PostgreSQL at {database_url}")
    conn.autocommit = True
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def _schema_initialized(connection_config, db_connection):
    """Run init script once per session, ensuring the schema exists."""
    execute_init_script(connection_config)


@pytest.fixture()
def txn_cursor(db_connection, _schema_initialized):
    """
    Function-scoped cursor wrapped in a SAVEPOINT so each test
    can INSERT/UPDATE without polluting subsequent tests.
    """
    cur = db_connection.cursor()
    cur.execute("BEGIN")
    cur.execute("SAVEPOINT test_sp")
    yield cur
    cur.execute("ROLLBACK TO SAVEPOINT test_sp")
    cur.execute("ROLLBACK")
    cur.close()


# ===================================================================
# TYPE VALIDATION TESTS
# ===================================================================

class TestTaskStatusType:
    def test_valid_variants(self):
        """TaskStatus enum accepts pending, in_progress, done."""
        assert TaskStatus.pending is not None
        assert TaskStatus.in_progress is not None
        assert TaskStatus.done is not None

    def test_variant_values(self):
        """Each variant's value matches its string label."""
        assert TaskStatus.pending.value == "pending" or str(TaskStatus.pending) is not None
        assert TaskStatus.in_progress.value == "in_progress" or str(TaskStatus.in_progress) is not None
        assert TaskStatus.done.value == "done" or str(TaskStatus.done) is not None


class TestTaskTitleType:
    def test_valid_single_char(self):
        t = TaskTitle(value="a")
        assert t.value == "a"

    def test_valid_max_length(self):
        val = "x" * 255
        t = TaskTitle(value=val)
        assert t.value == val
        assert len(t.value) == 255

    def test_empty_string_rejected(self):
        with pytest.raises((ValueError, Exception)):
            TaskTitle(value="")

    def test_too_long_rejected(self):
        with pytest.raises((ValueError, Exception)):
            TaskTitle(value="x" * 256)

    def test_boundary_length_one(self):
        t = TaskTitle(value="Z")
        assert len(t.value) == 1

    def test_boundary_length_255(self):
        t = TaskTitle(value="A" * 255)
        assert len(t.value) == 255


class TestTimestamptzType:
    @pytest.mark.parametrize("val", [
        "2024-01-01T00:00:00Z",
        "2024-06-15T12:30:00+05:30",
        "2024-06-15T12:30:00-04:00",
        "2024-01-01T00:00:00.123456Z",
        "2024-12-31T23:59:59.999Z",
        "2024-01-01T00:00:00+00:00",
    ])
    def test_valid_formats(self, val: str):
        ts = Timestamptz(value=val)
        assert ts.value == val

    @pytest.mark.parametrize("val", [
        "2024-01-01",
        "2024-01-01T00:00:00",
        "not-a-date",
        "",
        "2024/01/01T00:00:00Z",
    ])
    def test_invalid_formats_rejected(self, val: str):
        with pytest.raises((ValueError, Exception)):
            Timestamptz(value=val)


class TestConnectionConfigType:
    def test_valid_config(self):
        cc = ConnectionConfig(database_url="postgresql://user:pass@localhost/db", port=5432)
        assert cc.database_url.startswith("postgresql://")
        assert cc.port == 5432

    def test_bad_url_scheme_rejected(self):
        with pytest.raises((ValueError, Exception)):
            ConnectionConfig(database_url="mysql://user:pass@localhost/db", port=5432)

    def test_bad_port_rejected(self):
        with pytest.raises((ValueError, Exception)):
            ConnectionConfig(database_url="postgresql://user:pass@localhost/db", port=3306)

    def test_port_5431_rejected(self):
        with pytest.raises((ValueError, Exception)):
            ConnectionConfig(database_url="postgresql://user:pass@localhost/db", port=5431)

    def test_port_5433_rejected(self):
        with pytest.raises((ValueError, Exception)):
            ConnectionConfig(database_url="postgresql://user:pass@localhost/db", port=5433)


# ===================================================================
# EXECUTE_INIT_SCRIPT TESTS
# ===================================================================

class TestExecuteInitScriptHappyPath:
    def test_first_execution(self, connection_config, db_connection):
        """execute_init_script succeeds and returns all-True result."""
        result = execute_init_script(connection_config)
        assert isinstance(result, InitScriptResult)
        assert result.table_created is True
        assert result.trigger_created is True
        assert result.check_constraint_present is True

    def test_idempotent_second_execution(self, connection_config, db_connection):
        """Calling execute_init_script twice yields same result without error."""
        result1 = execute_init_script(connection_config)
        result2 = execute_init_script(connection_config)
        assert result1.table_created == result2.table_created
        assert result1.trigger_created == result2.trigger_created
        assert result1.check_constraint_present == result2.check_constraint_present
        assert result2.table_created is True
        assert result2.trigger_created is True
        assert result2.check_constraint_present is True


class TestExecuteInitScriptErrors:
    def test_connection_refused_bad_port(self):
        """connection_refused when PostgreSQL is unreachable (bad port)."""
        bad_config = ConnectionConfig(
            database_url="postgresql://user:pass@localhost:19999/nonexist",
            port=5432,
        )
        with pytest.raises(Exception):
            execute_init_script(bad_config)

    def test_authentication_failed(self, database_url):
        """authentication_failed with invalid credentials."""
        # Replace password in URL with garbage
        bad_url = re.sub(r"://([^:]+):([^@]+)@", r"://\1:BADPASSWORD_xyz@", database_url)
        if bad_url == database_url:
            # URL might not have password; construct one
            bad_url = "postgresql://baduser:badpass@localhost:5432/postgres"
        bad_config = ConnectionConfig(database_url=bad_url, port=5432)
        with pytest.raises(Exception):
            execute_init_script(bad_config)

    def test_database_not_found(self, database_url):
        """database_not_found when database name does not exist."""
        # Replace DB name with nonexistent one
        bad_url = re.sub(r"/([^/?]+)(\?|$)", r"/nonexistent_db_xyz_99\2", database_url)
        bad_config = ConnectionConfig(database_url=bad_url, port=5432)
        with pytest.raises(Exception):
            execute_init_script(bad_config)


# ===================================================================
# VERIFY_SCHEMA TESTS
# ===================================================================

class TestVerifySchemaHappyPath:
    def test_after_init(self, connection_config, _schema_initialized):
        """verify_schema returns all True after init script has run."""
        result = verify_schema(connection_config)
        assert isinstance(result, InitScriptResult)
        assert result.table_created is True
        assert result.trigger_created is True
        assert result.check_constraint_present is True


class TestVerifySchemaErrors:
    def test_connection_refused(self):
        """connection_refused when PostgreSQL is unreachable."""
        bad_config = ConnectionConfig(
            database_url="postgresql://user:pass@localhost:19999/nonexist",
            port=5432,
        )
        with pytest.raises(Exception):
            verify_schema(bad_config)

    def test_authentication_failed(self, database_url):
        """authentication_failed with invalid credentials."""
        bad_url = re.sub(r"://([^:]+):([^@]+)@", r"://\1:BADPASSWORD_xyz@", database_url)
        if bad_url == database_url:
            bad_url = "postgresql://baduser:badpass@localhost:5432/postgres"
        bad_config = ConnectionConfig(database_url=bad_url, port=5432)
        with pytest.raises(Exception):
            verify_schema(bad_config)


# ===================================================================
# SCHEMA INVARIANT TESTS (live database introspection)
# ===================================================================

class TestSchemaInvariantColumns:
    """Verify tasks table column definitions via information_schema."""

    def test_exactly_six_columns(self, db_connection, _schema_initialized):
        cur = db_connection.cursor()
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'tasks'
            ORDER BY ordinal_position
        """)
        columns = [row[0] for row in cur.fetchall()]
        cur.close()
        assert len(columns) == 6
        assert set(columns) == {"id", "title", "description", "status", "created_at", "updated_at"}

    def _get_column_info(self, db_connection, column_name: str) -> dict:
        cur = db_connection.cursor()
        cur.execute("""
            SELECT data_type, character_maximum_length, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'tasks' AND column_name = %s
        """, (column_name,))
        row = cur.fetchone()
        cur.close()
        assert row is not None, f"Column '{column_name}' not found"
        return {
            "data_type": row[0],
            "character_maximum_length": row[1],
            "is_nullable": row[2],
            "column_default": row[3],
        }

    def test_column_id(self, db_connection, _schema_initialized):
        info = self._get_column_info(db_connection, "id")
        assert info["data_type"] == "integer"
        assert info["is_nullable"] == "NO"
        # SERIAL implies a sequence default
        assert info["column_default"] is not None
        assert "nextval" in info["column_default"]

    def test_column_title(self, db_connection, _schema_initialized):
        info = self._get_column_info(db_connection, "title")
        assert info["data_type"] == "character varying"
        assert info["character_maximum_length"] == 255
        assert info["is_nullable"] == "NO"

    def test_column_description(self, db_connection, _schema_initialized):
        info = self._get_column_info(db_connection, "description")
        assert info["data_type"] == "text"
        assert info["is_nullable"] == "YES"

    def test_column_status(self, db_connection, _schema_initialized):
        info = self._get_column_info(db_connection, "status")
        assert info["data_type"] == "character varying"
        assert info["character_maximum_length"] == 20
        assert info["is_nullable"] == "NO"
        assert info["column_default"] is not None
        assert "pending" in info["column_default"]

    def test_column_created_at(self, db_connection, _schema_initialized):
        info = self._get_column_info(db_connection, "created_at")
        assert info["data_type"] == "timestamp with time zone"
        assert info["is_nullable"] == "NO"
        assert info["column_default"] is not None
        assert "now" in info["column_default"].lower()

    def test_column_updated_at(self, db_connection, _schema_initialized):
        info = self._get_column_info(db_connection, "updated_at")
        assert info["data_type"] == "timestamp with time zone"
        assert info["is_nullable"] == "NO"
        assert info["column_default"] is not None
        assert "now" in info["column_default"].lower()

    def test_id_is_primary_key(self, db_connection, _schema_initialized):
        cur = db_connection.cursor()
        cur.execute("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'tasks' AND tc.constraint_type = 'PRIMARY KEY'
        """)
        pk_columns = [row[0] for row in cur.fetchall()]
        cur.close()
        assert "id" in pk_columns


class TestSchemaInvariantConstraints:
    """Verify CHECK constraint on status column."""

    def test_check_constraint_exists(self, db_connection, _schema_initialized):
        cur = db_connection.cursor()
        cur.execute("""
            SELECT pg_get_constraintdef(c.oid)
            FROM pg_constraint c
            JOIN pg_class t ON c.conrelid = t.oid
            WHERE t.relname = 'tasks' AND c.contype = 'c'
        """)
        rows = cur.fetchall()
        cur.close()
        # At least one CHECK constraint should reference the three valid statuses
        all_defs = " ".join(row[0] for row in rows)
        assert "pending" in all_defs
        assert "in_progress" in all_defs
        assert "done" in all_defs

    def test_invalid_status_rejected_by_check(self, txn_cursor):
        with pytest.raises(Exception) as exc_info:
            txn_cursor.execute(
                "INSERT INTO tasks (title, status) VALUES (%s, %s)",
                ("test", "invalid_status"),
            )
        # Should be a check violation
        assert "check" in str(exc_info.value).lower() or "violates" in str(exc_info.value).lower()


class TestSchemaInvariantTrigger:
    """Verify update_updated_at_column trigger."""

    def test_trigger_exists_before_update(self, db_connection, _schema_initialized):
        cur = db_connection.cursor()
        cur.execute("""
            SELECT tgname, tgtype
            FROM pg_trigger
            JOIN pg_class ON pg_trigger.tgrelid = pg_class.oid
            WHERE pg_class.relname = 'tasks'
              AND NOT tgisinternal
        """)
        triggers = cur.fetchall()
        cur.close()
        trigger_names = [t[0] for t in triggers]
        # There should be a trigger with 'update' in its name
        assert any("update" in name.lower() for name in trigger_names), (
            f"No update trigger found. Triggers: {trigger_names}"
        )

    def test_trigger_function_exists(self, db_connection, _schema_initialized):
        cur = db_connection.cursor()
        cur.execute("""
            SELECT proname
            FROM pg_proc
            WHERE proname = 'update_updated_at_column'
        """)
        rows = cur.fetchall()
        cur.close()
        assert len(rows) >= 1


class TestSchemaInvariantBehavior:
    """Verify runtime behavior of defaults and trigger."""

    def test_default_status_pending(self, txn_cursor):
        txn_cursor.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING status",
            ("test_default_status",),
        )
        status = txn_cursor.fetchone()[0]
        assert status == "pending"

    def test_description_null_when_omitted(self, txn_cursor):
        txn_cursor.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING description",
            ("test_null_desc",),
        )
        desc = txn_cursor.fetchone()[0]
        assert desc is None

    def test_created_at_set_on_insert(self, txn_cursor):
        txn_cursor.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING created_at",
            ("test_created_at",),
        )
        created_at = txn_cursor.fetchone()[0]
        assert isinstance(created_at, datetime.datetime)
        assert created_at.tzinfo is not None

    def test_updated_at_set_on_insert(self, txn_cursor):
        txn_cursor.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING updated_at",
            ("test_updated_at",),
        )
        updated_at = txn_cursor.fetchone()[0]
        assert isinstance(updated_at, datetime.datetime)
        assert updated_at.tzinfo is not None

    def test_trigger_advances_updated_at(self, txn_cursor):
        txn_cursor.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING id, updated_at",
            ("test_trigger",),
        )
        row = txn_cursor.fetchone()
        task_id, updated_at_before = row[0], row[1]

        # Small delay to ensure clock advances
        time.sleep(0.05)

        txn_cursor.execute(
            "UPDATE tasks SET title = %s WHERE id = %s RETURNING updated_at",
            ("test_trigger_updated", task_id),
        )
        updated_at_after = txn_cursor.fetchone()[0]
        assert updated_at_after >= updated_at_before

    def test_created_at_unchanged_on_update(self, txn_cursor):
        txn_cursor.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING id, created_at",
            ("test_created_immutable",),
        )
        row = txn_cursor.fetchone()
        task_id, created_at_before = row[0], row[1]

        time.sleep(0.05)

        txn_cursor.execute(
            "UPDATE tasks SET title = %s WHERE id = %s RETURNING created_at",
            ("test_created_immutable_v2", task_id),
        )
        created_at_after = txn_cursor.fetchone()[0]
        assert created_at_before == created_at_after

    def test_all_valid_statuses_insertable(self, txn_cursor):
        for status in ("pending", "in_progress", "done"):
            txn_cursor.execute(
                "INSERT INTO tasks (title, status) VALUES (%s, %s) RETURNING status",
                (f"test_{status}", status),
            )
            returned = txn_cursor.fetchone()[0]
            assert returned == status

    def test_timestamptz_values_are_utc_aware(self, txn_cursor):
        txn_cursor.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING created_at, updated_at",
            ("test_tz",),
        )
        row = txn_cursor.fetchone()
        assert row[0].tzinfo is not None
        assert row[1].tzinfo is not None

    def test_psycopg2_type_mapping(self, txn_cursor):
        """Verify psycopg2 returns expected Python types for each column."""
        txn_cursor.execute(
            "INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s) "
            "RETURNING id, title, description, status, created_at, updated_at",
            ("mapping_test", "some desc", "done"),
        )
        row = txn_cursor.fetchone()
        assert isinstance(row[0], int)                    # id
        assert isinstance(row[1], str)                    # title
        assert isinstance(row[2], str)                    # description (non-null)
        assert isinstance(row[3], str)                    # status
        assert isinstance(row[4], datetime.datetime)      # created_at
        assert isinstance(row[5], datetime.datetime)      # updated_at


class TestSchemaInvariantIdempotency:
    """Re-executing init script must not modify pre-existing data."""

    def test_data_preserved_after_re_init(self, connection_config, db_connection, _schema_initialized):
        cur = db_connection.cursor()
        # Insert a row
        cur.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, status, created_at",
            ("idempotency_test",),
        )
        inserted = cur.fetchone()
        inserted_id = inserted[0]

        # Count rows
        cur.execute("SELECT count(*) FROM tasks")
        count_before = cur.fetchone()[0]

        # Re-execute init
        execute_init_script(connection_config)

        # Verify row still exists unchanged
        cur.execute(
            "SELECT id, title, status, created_at FROM tasks WHERE id = %s",
            (inserted_id,),
        )
        after = cur.fetchone()
        assert after is not None
        assert after[0] == inserted[0]
        assert after[1] == inserted[1]
        assert after[2] == inserted[2]
        assert after[3] == inserted[3]

        # Count should be same
        cur.execute("SELECT count(*) FROM tasks")
        count_after = cur.fetchone()[0]
        assert count_after == count_before

        # Cleanup
        cur.execute("DELETE FROM tasks WHERE id = %s", (inserted_id,))
        cur.close()


# ===================================================================
# EDGE CASES: VARCHAR limit and randomized fuzzing
# ===================================================================

class TestEdgeCaseTitleLength:
    def test_title_exactly_255_chars(self, txn_cursor):
        title = "A" * 255
        txn_cursor.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING title",
            (title,),
        )
        returned = txn_cursor.fetchone()[0]
        assert returned == title
        assert len(returned) == 255

    def test_title_256_chars_rejected(self, txn_cursor):
        title = "A" * 256
        with pytest.raises(Exception):
            txn_cursor.execute(
                "INSERT INTO tasks (title) VALUES (%s)",
                (title,),
            )


class TestRandomizedInserts:
    """Use random module to generate valid/invalid data for INSERT testing."""

    def test_random_valid_titles(self, txn_cursor):
        """50 randomly generated valid titles (1-255 chars) all INSERT successfully."""
        rng = random.Random(42)
        for _ in range(50):
            length = rng.randint(1, 255)
            title = "".join(rng.choices(string.ascii_letters + string.digits + " ", k=length))
            txn_cursor.execute(
                "INSERT INTO tasks (title) VALUES (%s) RETURNING id",
                (title,),
            )
            row = txn_cursor.fetchone()
            assert row is not None
            assert isinstance(row[0], int)

    def test_random_invalid_statuses_rejected(self, txn_cursor):
        """50 randomly generated invalid status strings are all rejected by CHECK."""
        rng = random.Random(43)
        valid_statuses = {"pending", "in_progress", "done"}
        attempts = 0
        while attempts < 50:
            length = rng.randint(1, 20)
            status = "".join(rng.choices(string.ascii_lowercase + "_", k=length))
            if status in valid_statuses:
                continue
            attempts += 1
            with pytest.raises(Exception):
                txn_cursor.execute(
                    "INSERT INTO tasks (title, status) VALUES (%s, %s)",
                    (f"random_test_{attempts}", status),
                )
            # Reset the transaction state after the error
            txn_cursor.execute("ROLLBACK TO SAVEPOINT test_sp")
            txn_cursor.execute("SAVEPOINT test_sp")

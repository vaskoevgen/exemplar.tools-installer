"""
Adversarial hidden acceptance tests for PostgreSQL Database Schema component.
These tests target gaps in visible test coverage and detect implementations
that might hardcode returns or take shortcuts.
"""

import pytest
import time
import datetime
import os
import psycopg2

from database import (
    execute_init_script,
    verify_schema,
    TaskStatus,
    TaskTitle,
    TaskDescription,
    Timestamptz,
    ConnectionConfig,
    InitScriptResult,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_config():
    """Return a valid ConnectionConfig from the environment."""
    url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/testdb")
    return ConnectionConfig(database_url=url, port=5432)


def _get_conn():
    """Return a raw psycopg2 connection for direct SQL verification."""
    url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/testdb")
    return psycopg2.connect(url)


def _init():
    """Run execute_init_script and return the config."""
    cfg = _get_config()
    execute_init_script(cfg)
    return cfg


def _clean_tasks():
    """Delete all rows from tasks table."""
    conn = _get_conn()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks")
    cur.close()
    conn.close()


# ===========================================================================
# Type Validation Tests
# ===========================================================================

class TestGoodhartConnectionConfig:

    def test_goodhart_connection_config_port_5431_rejected(self):
        """ConnectionConfig must reject port values adjacent to valid — port 5431 is not 5432."""
        with pytest.raises(Exception):
            ConnectionConfig(database_url="postgresql://user:pass@localhost/db", port=5431)

    def test_goodhart_connection_config_port_5433_rejected(self):
        """ConnectionConfig must reject port 5433 — only exactly 5432 is valid."""
        with pytest.raises(Exception):
            ConnectionConfig(database_url="postgresql://user:pass@localhost/db", port=5433)

    def test_goodhart_connection_config_port_0_rejected(self):
        """ConnectionConfig must reject port 0."""
        with pytest.raises(Exception):
            ConnectionConfig(database_url="postgresql://user:pass@localhost/db", port=0)

    def test_goodhart_connection_config_port_negative_rejected(self):
        """ConnectionConfig must reject negative port values."""
        with pytest.raises(Exception):
            ConnectionConfig(database_url="postgresql://user:pass@localhost/db", port=-1)

    def test_goodhart_connection_config_postgres_scheme_rejected(self):
        """ConnectionConfig must reject 'postgres://' — only 'postgresql://' prefix is valid."""
        with pytest.raises(Exception):
            ConnectionConfig(database_url="postgres://user:pass@localhost/db", port=5432)

    def test_goodhart_connection_config_mysql_scheme_rejected(self):
        """ConnectionConfig must reject non-postgresql schemes like mysql://."""
        with pytest.raises(Exception):
            ConnectionConfig(database_url="mysql://user:pass@localhost/db", port=5432)

    def test_goodhart_connection_config_empty_url_rejected(self):
        """ConnectionConfig must reject empty string URL."""
        with pytest.raises(Exception):
            ConnectionConfig(database_url="", port=5432)


class TestGoodhartTaskStatus:

    def test_goodhart_task_status_rejects_substring(self):
        """TaskStatus must reject strings that are substrings of valid values."""
        for invalid in ["pend", "pendin", "in_prog", "in_progres", "don", "do"]:
            with pytest.raises(Exception):
                TaskStatus(invalid)

    def test_goodhart_task_status_rejects_superstring(self):
        """TaskStatus must reject strings that are superstrings of valid values."""
        for invalid in ["pendings", "in_progress_", "done!", "pending "]:
            with pytest.raises(Exception):
                TaskStatus(invalid)

    def test_goodhart_task_status_rejects_empty_string(self):
        """TaskStatus must reject empty string."""
        with pytest.raises(Exception):
            TaskStatus("")

    def test_goodhart_task_status_case_sensitive(self):
        """TaskStatus must be case-sensitive — uppercase/mixed-case variants are invalid."""
        for invalid in ["Pending", "PENDING", "In_Progress", "IN_PROGRESS", "Done", "DONE"]:
            with pytest.raises(Exception):
                TaskStatus(invalid)


class TestGoodhartTaskTitle:

    def test_goodhart_task_title_length_254_accepted(self):
        """TaskTitle must accept boundary-adjacent length of 254 characters."""
        title = TaskTitle(value="a" * 254)
        assert len(title.value) == 254

    def test_goodhart_task_title_length_2_accepted(self):
        """TaskTitle must accept length 2 — not just boundary values 1 and 255."""
        title = TaskTitle(value="ab")
        assert title.value == "ab"

    def test_goodhart_task_title_length_1_accepted(self):
        """TaskTitle must accept exactly 1 character."""
        title = TaskTitle(value="x")
        assert title.value == "x"

    def test_goodhart_task_title_whitespace_only_accepted(self):
        """TaskTitle of all spaces should be accepted by schema (length >= 1)."""
        title = TaskTitle(value="   ")
        assert len(title.value) == 3

    def test_goodhart_task_title_length_257_rejected(self):
        """TaskTitle must reject length 257, not just 256."""
        with pytest.raises(Exception):
            TaskTitle(value="a" * 257)

    def test_goodhart_task_title_length_1000_rejected(self):
        """TaskTitle must reject very long strings well beyond 255."""
        with pytest.raises(Exception):
            TaskTitle(value="a" * 1000)


class TestGoodhartTimestamptz:

    def test_goodhart_timestamptz_fractional_1_digit(self):
        """Timestamptz must accept 1 fractional second digit."""
        ts = Timestamptz(value="2024-01-01T00:00:00.1Z")
        assert ts.value == "2024-01-01T00:00:00.1Z"

    def test_goodhart_timestamptz_fractional_6_digits(self):
        """Timestamptz must accept 6 fractional second digits."""
        ts = Timestamptz(value="2024-01-01T00:00:00.123456Z")
        assert ts.value == "2024-01-01T00:00:00.123456Z"

    def test_goodhart_timestamptz_positive_offset(self):
        """Timestamptz must accept positive UTC offsets."""
        ts = Timestamptz(value="2024-06-15T14:30:00+05:30")
        assert ts.value == "2024-06-15T14:30:00+05:30"

    def test_goodhart_timestamptz_negative_offset(self):
        """Timestamptz must accept negative UTC offsets."""
        ts = Timestamptz(value="2024-06-15T14:30:00-07:00")
        assert ts.value == "2024-06-15T14:30:00-07:00"

    def test_goodhart_timestamptz_no_T_separator_rejected(self):
        """Timestamptz must reject space-separated datetime strings."""
        with pytest.raises(Exception):
            Timestamptz(value="2024-01-01 00:00:00Z")

    def test_goodhart_timestamptz_date_only_rejected(self):
        """Timestamptz must reject date-only strings."""
        with pytest.raises(Exception):
            Timestamptz(value="2024-01-01Z")

    def test_goodhart_timestamptz_no_timezone_rejected(self):
        """Timestamptz must reject timestamps without any timezone indicator."""
        with pytest.raises(Exception):
            Timestamptz(value="2024-01-01T00:00:00")

    def test_goodhart_timestamptz_offset_without_colon_rejected(self):
        """Timestamptz must reject offsets without colon like +0530 (regex requires +HH:MM)."""
        with pytest.raises(Exception):
            Timestamptz(value="2024-01-01T00:00:00+0530")


# ===========================================================================
# Schema & Data Behavior Tests (require live PostgreSQL)
# ===========================================================================

class TestGoodhartSchemaInvariants:

    def test_goodhart_select_star_returns_all_six_columns(self):
        """SELECT * must return exactly the six expected column names."""
        _init()
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks")
        cur.execute("INSERT INTO tasks (title) VALUES ('col_test')")
        cur.execute("SELECT * FROM tasks WHERE title = 'col_test'")
        col_names = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()
        assert set(col_names) == {"id", "title", "description", "status", "created_at", "updated_at"}
        assert len(col_names) == 6

    def test_goodhart_primary_key_prevents_duplicate_id(self):
        """PRIMARY KEY on id must prevent manual insertion of duplicate id values."""
        _init()
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title) VALUES ('pk_test') RETURNING id")
        row_id = cur.fetchone()[0]
        with pytest.raises(psycopg2.errors.UniqueViolation):
            cur.execute("INSERT INTO tasks (id, title) VALUES (%s, 'dup')", (row_id,))
        conn.rollback()
        cur.execute("DELETE FROM tasks WHERE title IN ('pk_test', 'dup')")
        cur.close()
        conn.close()

    def test_goodhart_id_autoincrement_unique(self):
        """Auto-increment must produce distinct integer ids for multiple inserts."""
        _init()
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        ids = []
        for i in range(3):
            cur.execute("INSERT INTO tasks (title) VALUES (%s) RETURNING id", (f"auto_{i}",))
            ids.append(cur.fetchone()[0])
        cur.execute("DELETE FROM tasks WHERE title LIKE 'auto_%%'")
        cur.close()
        conn.close()
        assert len(set(ids)) == 3
        for _id in ids:
            assert isinstance(_id, int)

    def test_goodhart_id_gaps_after_failed_insert(self):
        """SERIAL sequence advances even on failed inserts, producing non-contiguous ids."""
        _init()
        conn = _get_conn()
        conn.autocommit = False
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO tasks (title) VALUES ('gap_before') RETURNING id")
            id_before = cur.fetchone()[0]
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        # This insert should fail due to CHECK constraint on status
        try:
            cur.execute("INSERT INTO tasks (title, status) VALUES ('gap_fail', 'invalid_xyz')")
            conn.commit()
        except Exception:
            conn.rollback()
        try:
            cur.execute("INSERT INTO tasks (title) VALUES ('gap_after') RETURNING id")
            id_after = cur.fetchone()[0]
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        # The gap may or may not be exactly 1, but both ids should be valid ints
        assert isinstance(id_before, int)
        assert isinstance(id_after, int)
        assert id_after > id_before
        # Clean up
        cur.execute("DELETE FROM tasks WHERE title IN ('gap_before', 'gap_after')")
        conn.commit()
        cur.close()
        conn.close()


class TestGoodhartTriggerBehavior:

    def test_goodhart_trigger_updates_only_updated_at(self):
        """Trigger must only modify updated_at, not any other column."""
        _init()
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (title, description, status) VALUES ('orig_title', 'orig_desc', 'pending') RETURNING id, title, description, status, created_at"
        )
        row = cur.fetchone()
        row_id, orig_title, orig_desc, orig_status, orig_created = row
        time.sleep(0.05)
        cur.execute("UPDATE tasks SET title = 'new_title' WHERE id = %s", (row_id,))
        cur.execute("SELECT title, description, status, created_at FROM tasks WHERE id = %s", (row_id,))
        new_row = cur.fetchone()
        assert new_row[0] == "new_title"  # title was explicitly changed
        assert new_row[1] == orig_desc  # description unchanged
        assert new_row[2] == orig_status  # status unchanged
        assert new_row[3] == orig_created  # created_at unchanged by trigger
        cur.execute("DELETE FROM tasks WHERE id = %s", (row_id,))
        cur.close()
        conn.close()

    def test_goodhart_multiple_updates_advance_updated_at(self):
        """Each successive UPDATE must advance updated_at — trigger fires every time."""
        _init()
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title) VALUES ('multi_update') RETURNING id, updated_at")
        row_id, ts0 = cur.fetchone()
        time.sleep(0.05)
        cur.execute("UPDATE tasks SET title = 'multi_update_1' WHERE id = %s", (row_id,))
        cur.execute("SELECT updated_at FROM tasks WHERE id = %s", (row_id,))
        ts1 = cur.fetchone()[0]
        time.sleep(0.05)
        cur.execute("UPDATE tasks SET title = 'multi_update_2' WHERE id = %s", (row_id,))
        cur.execute("SELECT updated_at FROM tasks WHERE id = %s", (row_id,))
        ts2 = cur.fetchone()[0]
        assert ts1 >= ts0
        assert ts2 >= ts1
        # At least one of the advances should be strictly greater (with sleep)
        assert ts2 > ts0
        cur.execute("DELETE FROM tasks WHERE id = %s", (row_id,))
        cur.close()
        conn.close()

    def test_goodhart_update_status_triggers_updated_at(self):
        """Updating status column must also trigger updated_at advancement."""
        _init()
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title) VALUES ('status_trigger_test') RETURNING id, updated_at")
        row_id, ts_insert = cur.fetchone()
        time.sleep(0.05)
        cur.execute("UPDATE tasks SET status = 'in_progress' WHERE id = %s", (row_id,))
        cur.execute("SELECT status, updated_at FROM tasks WHERE id = %s", (row_id,))
        status, ts_after = cur.fetchone()
        assert status == "in_progress"
        assert ts_after > ts_insert
        cur.execute("DELETE FROM tasks WHERE id = %s", (row_id,))
        cur.close()
        conn.close()

    def test_goodhart_update_description_null_to_value_triggers(self):
        """Updating description from NULL to a value must trigger updated_at change."""
        _init()
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title) VALUES ('desc_trigger') RETURNING id, updated_at")
        row_id, ts_insert = cur.fetchone()
        time.sleep(0.05)
        cur.execute("UPDATE tasks SET description = 'now has desc' WHERE id = %s", (row_id,))
        cur.execute("SELECT description, updated_at FROM tasks WHERE id = %s", (row_id,))
        desc, ts_after = cur.fetchone()
        assert desc == "now has desc"
        assert ts_after > ts_insert
        cur.execute("DELETE FROM tasks WHERE id = %s", (row_id,))
        cur.close()
        conn.close()


class TestGoodhartNullAndDefault:

    def test_goodhart_null_title_rejected(self):
        """NOT NULL constraint on title must reject NULL title insertion."""
        _init()
        conn = _get_conn()
        conn.autocommit = False
        cur = conn.cursor()
        with pytest.raises(psycopg2.errors.NotNullViolation):
            cur.execute("INSERT INTO tasks (title) VALUES (NULL)")
        conn.rollback()
        cur.close()
        conn.close()

    def test_goodhart_explicit_null_status_rejected(self):
        """Explicitly setting status=NULL must be rejected by NOT NULL constraint even though DEFAULT exists."""
        _init()
        conn = _get_conn()
        conn.autocommit = False
        cur = conn.cursor()
        with pytest.raises(psycopg2.errors.NotNullViolation):
            cur.execute("INSERT INTO tasks (title, status) VALUES ('null_status_test', NULL)")
        conn.rollback()
        cur.close()
        conn.close()

    def test_goodhart_description_empty_string_vs_null(self):
        """Empty string description and NULL description are distinct stored values."""
        _init()
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title, description) VALUES ('with_empty', '') RETURNING id")
        id_empty = cur.fetchone()[0]
        cur.execute("INSERT INTO tasks (title) VALUES ('with_null') RETURNING id")
        id_null = cur.fetchone()[0]
        cur.execute("SELECT description FROM tasks WHERE id = %s", (id_empty,))
        desc_empty = cur.fetchone()[0]
        cur.execute("SELECT description FROM tasks WHERE id = %s", (id_null,))
        desc_null = cur.fetchone()[0]
        assert desc_empty == ""
        assert desc_null is None
        assert desc_empty != desc_null
        cur.execute("DELETE FROM tasks WHERE id IN (%s, %s)", (id_empty, id_null))
        cur.close()
        conn.close()

    def test_goodhart_empty_string_title_allowed_by_schema(self):
        """Empty string '' is allowed by database schema for title (VARCHAR NOT NULL allows it)."""
        _init()
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title) VALUES ('') RETURNING id")
        row_id = cur.fetchone()[0]
        cur.execute("SELECT title FROM tasks WHERE id = %s", (row_id,))
        title = cur.fetchone()[0]
        assert title == ""
        cur.execute("DELETE FROM tasks WHERE id = %s", (row_id,))
        cur.close()
        conn.close()

    def test_goodhart_created_at_and_updated_at_equal_on_insert(self):
        """On fresh INSERT, created_at and updated_at should be equal (both DEFAULT NOW())."""
        _init()
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title) VALUES ('ts_eq_test') RETURNING id, created_at, updated_at")
        row_id, created_at, updated_at = cur.fetchone()
        assert created_at == updated_at
        cur.execute("DELETE FROM tasks WHERE id = %s", (row_id,))
        cur.close()
        conn.close()


class TestGoodhartStatusConstraint:

    def test_goodhart_status_case_sensitive(self):
        """CHECK constraint on status is case-sensitive — mixed-case variants must be rejected."""
        _init()
        conn = _get_conn()
        conn.autocommit = False
        cur = conn.cursor()
        for bad_status in ["Pending", "PENDING", "In_Progress", "IN_PROGRESS", "Done", "DONE"]:
            try:
                cur.execute("INSERT INTO tasks (title, status) VALUES ('case_test', %s)", (bad_status,))
                conn.commit()
                pytest.fail(f"Status '{bad_status}' should have been rejected")
            except psycopg2.errors.CheckViolation:
                conn.rollback()
            except Exception:
                conn.rollback()
                raise
        cur.close()
        conn.close()

    def test_goodhart_status_whitespace_rejected(self):
        """Status values with whitespace padding must be rejected."""
        _init()
        conn = _get_conn()
        conn.autocommit = False
        cur = conn.cursor()
        for bad_status in [" pending", "pending ", " done ", "in_progress "]:
            try:
                cur.execute("INSERT INTO tasks (title, status) VALUES ('ws_test', %s)", (bad_status,))
                conn.commit()
                pytest.fail(f"Status '{bad_status}' should have been rejected")
            except psycopg2.errors.CheckViolation:
                conn.rollback()
            except Exception:
                conn.rollback()
                raise
        cur.close()
        conn.close()

    def test_goodhart_status_empty_string_rejected(self):
        """Empty string status must be rejected by CHECK constraint."""
        _init()
        conn = _get_conn()
        conn.autocommit = False
        cur = conn.cursor()
        with pytest.raises(psycopg2.errors.CheckViolation):
            cur.execute("INSERT INTO tasks (title, status) VALUES ('empty_status', '')")
        conn.rollback()
        cur.close()
        conn.close()


class TestGoodhartPsycopg2TypeMapping:

    def test_goodhart_psycopg2_id_is_int(self):
        """psycopg2 must map id column to Python int."""
        _init()
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title) VALUES ('type_test') RETURNING id")
        row_id = cur.fetchone()[0]
        assert type(row_id) is int
        cur.execute("DELETE FROM tasks WHERE id = %s", (row_id,))
        cur.close()
        conn.close()

    def test_goodhart_psycopg2_title_is_str(self):
        """psycopg2 must map title column to Python str."""
        _init()
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title) VALUES ('type_str_test') RETURNING id")
        row_id = cur.fetchone()[0]
        cur.execute("SELECT title FROM tasks WHERE id = %s", (row_id,))
        title = cur.fetchone()[0]
        assert type(title) is str
        cur.execute("DELETE FROM tasks WHERE id = %s", (row_id,))
        cur.close()
        conn.close()

    def test_goodhart_psycopg2_description_none_type(self):
        """psycopg2 must map NULL description to Python None (NoneType)."""
        _init()
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title) VALUES ('none_desc') RETURNING id")
        row_id = cur.fetchone()[0]
        cur.execute("SELECT description FROM tasks WHERE id = %s", (row_id,))
        desc = cur.fetchone()[0]
        assert desc is None
        cur.execute("DELETE FROM tasks WHERE id = %s", (row_id,))
        cur.close()
        conn.close()

    def test_goodhart_psycopg2_datetime_aware_utc(self):
        """psycopg2 must return timezone-aware datetimes with UTC tzinfo for timestamp columns."""
        _init()
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title) VALUES ('tz_test') RETURNING id, created_at, updated_at")
        row_id, created_at, updated_at = cur.fetchone()
        assert isinstance(created_at, datetime.datetime)
        assert isinstance(updated_at, datetime.datetime)
        assert created_at.tzinfo is not None
        assert updated_at.tzinfo is not None
        # Verify UTC offset is 0
        assert created_at.utcoffset() == datetime.timedelta(0)
        assert updated_at.utcoffset() == datetime.timedelta(0)
        cur.execute("DELETE FROM tasks WHERE id = %s", (row_id,))
        cur.close()
        conn.close()


class TestGoodhartUnicodeAndEdge:

    def test_goodhart_unicode_title_insert(self):
        """Title column must support Unicode characters (CJK, emoji, accented)."""
        _init()
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        titles = ["任务标题", "tâche française", "🚀 Launch", "Ñoño", "данные"]
        ids = []
        for t in titles:
            cur.execute("INSERT INTO tasks (title) VALUES (%s) RETURNING id", (t,))
            ids.append(cur.fetchone()[0])
        for row_id, expected_title in zip(ids, titles):
            cur.execute("SELECT title FROM tasks WHERE id = %s", (row_id,))
            actual = cur.fetchone()[0]
            assert actual == expected_title, f"Expected '{expected_title}', got '{actual}'"
        for row_id in ids:
            cur.execute("DELETE FROM tasks WHERE id = %s", (row_id,))
        cur.close()
        conn.close()

    def test_goodhart_title_single_char_insert(self):
        """A single-character title must be insertable and retrievable."""
        _init()
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title) VALUES ('X') RETURNING id")
        row_id = cur.fetchone()[0]
        cur.execute("SELECT title FROM tasks WHERE id = %s", (row_id,))
        assert cur.fetchone()[0] == "X"
        cur.execute("DELETE FROM tasks WHERE id = %s", (row_id,))
        cur.close()
        conn.close()


class TestGoodhartIdempotency:

    def test_goodhart_idempotent_three_executions(self):
        """Init script must be idempotent beyond two runs — three consecutive executions must all succeed."""
        cfg = _get_config()
        r1 = execute_init_script(cfg)
        r2 = execute_init_script(cfg)
        r3 = execute_init_script(cfg)
        for r in [r1, r2, r3]:
            assert r.table_created is True
            assert r.trigger_created is True
            assert r.check_constraint_present is True

    def test_goodhart_idempotent_preserves_multiple_rows(self):
        """Re-executing init must preserve multiple pre-existing rows with diverse data."""
        cfg = _get_config()
        execute_init_script(cfg)
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        # Insert diverse rows
        test_data = [
            ("Task A", "Description A", "pending"),
            ("Task B", None, "in_progress"),
            ("Task C", "Desc C", "done"),
            ("Task D", "", "pending"),
            ("Task E", "Long " * 50, "in_progress"),
        ]
        ids = []
        for title, desc, status in test_data:
            if desc is not None:
                cur.execute(
                    "INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s) RETURNING id",
                    (title, desc, status),
                )
            else:
                cur.execute(
                    "INSERT INTO tasks (title, status) VALUES (%s, %s) RETURNING id",
                    (title, status),
                )
            ids.append(cur.fetchone()[0])
        # Snapshot before re-init
        cur.execute("SELECT id, title, description, status, created_at, updated_at FROM tasks WHERE id = ANY(%s) ORDER BY id", (ids,))
        before = cur.fetchall()
        cur.close()
        conn.close()

        # Re-execute init
        execute_init_script(cfg)

        # Verify all rows unchanged
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT id, title, description, status, created_at, updated_at FROM tasks WHERE id = ANY(%s) ORDER BY id", (ids,))
        after = cur.fetchall()
        assert before == after, "Re-init must not modify pre-existing rows"
        # Clean up
        for row_id in ids:
            cur.execute("DELETE FROM tasks WHERE id = %s", (row_id,))
        cur.close()
        conn.close()


class TestGoodhartVerifySchema:

    def test_goodhart_verify_schema_is_readonly(self):
        """verify_schema must not modify data — row count unchanged after call."""
        cfg = _get_config()
        execute_init_script(cfg)
        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title) VALUES ('readonly_test') RETURNING id")
        row_id = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM tasks")
        count_before = cur.fetchone()[0]
        cur.close()
        conn.close()

        verify_schema(cfg)

        conn = _get_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM tasks")
        count_after = cur.fetchone()[0]
        assert count_before == count_after
        cur.execute("DELETE FROM tasks WHERE id = %s", (row_id,))
        cur.close()
        conn.close()

    def test_goodhart_verify_schema_result_type(self):
        """verify_schema must return InitScriptResult with actual bool fields, not truthy/falsy."""
        cfg = _get_config()
        execute_init_script(cfg)
        result = verify_schema(cfg)
        assert type(result.table_created) is bool
        assert type(result.trigger_created) is bool
        assert type(result.check_constraint_present) is bool

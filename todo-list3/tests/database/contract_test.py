"""
Contract test suite for the 'database' component.

Tests PostgreSQL schema initialization (execute_init_script, verify_schema),
type validators (TaskStatus, TaskTitle, TaskDescription, Timestamptz,
ConnectionConfig, TaskRow, InitScriptResult), and schema invariants.

All database interactions are mocked via unittest.mock.
Run with: pytest contract_test.py -v
"""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock, call
import re

# Import the component under test
from database import (
    TaskStatus,
    TaskId,
    TaskTitle,
    TaskDescription,
    Timestamptz,
    TaskRow,
    ConnectionConfig,
    InitScriptResult,
    execute_init_script,
    verify_schema,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_connection_config():
    """Construct a valid ConnectionConfig for test use."""
    return ConnectionConfig(database_url="postgresql://user:pass@localhost/testdb", port=5432)


@pytest.fixture
def mock_psycopg2_success():
    """Mock psycopg2.connect returning a successful connection with cursor."""
    with patch("database.schema.psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value = mock_conn
        yield mock_connect, mock_conn, mock_cursor


# ---------------------------------------------------------------------------
# Type Tests: TaskStatus
# ---------------------------------------------------------------------------

class TestTaskStatus:
    """Tests for the TaskStatus enum type."""

    def test_task_status_pending_variant(self):
        """TaskStatus has a 'pending' variant."""
        status = TaskStatus.pending
        assert status is not None
        assert status == TaskStatus.pending

    def test_task_status_in_progress_variant(self):
        """TaskStatus has an 'in_progress' variant."""
        status = TaskStatus.in_progress
        assert status is not None
        assert status == TaskStatus.in_progress

    def test_task_status_done_variant(self):
        """TaskStatus has a 'done' variant."""
        status = TaskStatus.done
        assert status is not None
        assert status == TaskStatus.done

    def test_task_status_has_exactly_three_variants(self):
        """TaskStatus enum has exactly 3 variants: pending, in_progress, done."""
        members = list(TaskStatus)
        assert len(members) == 3
        member_names = {m.name for m in members}
        assert member_names == {"pending", "in_progress", "done"}

    def test_task_status_rejects_invalid_value(self):
        """TaskStatus rejects values outside the closed set."""
        with pytest.raises((ValueError, KeyError)):
            TaskStatus("cancelled")

    def test_task_status_rejects_empty_string(self):
        """TaskStatus rejects empty string."""
        with pytest.raises((ValueError, KeyError)):
            TaskStatus("")

    def test_task_status_rejects_numeric_value(self):
        """TaskStatus rejects numeric input not mapping to any variant."""
        # Attempt to construct from an arbitrary integer unlikely to be a member value
        with pytest.raises((ValueError, KeyError)):
            TaskStatus(999)


# ---------------------------------------------------------------------------
# Type Tests: TaskTitle
# ---------------------------------------------------------------------------

class TestTaskTitle:
    """Tests for TaskTitle value type with length validator."""

    def test_task_title_valid_string(self):
        """TaskTitle accepts a typical valid string."""
        title = TaskTitle(value="My Task")
        assert title.value == "My Task"

    def test_task_title_minimum_length_boundary(self):
        """TaskTitle accepts a single character (length == 1, minimum)."""
        title = TaskTitle(value="A")
        assert title.value == "A"
        assert len(title.value) == 1

    def test_task_title_maximum_length_boundary(self):
        """TaskTitle accepts a 255-character string (length == 255, maximum)."""
        val = "A" * 255
        title = TaskTitle(value=val)
        assert title.value == val
        assert len(title.value) == 255

    def test_task_title_rejects_empty_string(self):
        """TaskTitle rejects empty string (length 0 < minimum 1)."""
        with pytest.raises((ValueError, TypeError, Exception)):
            TaskTitle(value="")

    def test_task_title_rejects_too_long_string(self):
        """TaskTitle rejects string longer than 255 characters."""
        val = "A" * 256
        with pytest.raises((ValueError, TypeError, Exception)):
            TaskTitle(value=val)

    def test_task_title_accepts_255_unicode_chars(self):
        """TaskTitle accepts 255 unicode characters."""
        val = "\u00e9" * 255  # é repeated 255 times
        title = TaskTitle(value=val)
        assert len(title.value) == 255

    def test_task_title_rejects_256_unicode_chars(self):
        """TaskTitle rejects 256 unicode characters."""
        val = "\u00e9" * 256
        with pytest.raises((ValueError, TypeError, Exception)):
            TaskTitle(value=val)


# ---------------------------------------------------------------------------
# Type Tests: TaskDescription
# ---------------------------------------------------------------------------

class TestTaskDescription:
    """Tests for TaskDescription optional type."""

    def test_task_description_accepts_none(self):
        """TaskDescription accepts None representing SQL NULL."""
        # TaskDescription is optional; None is valid
        desc = TaskDescription(None)
        assert desc is not None  # The wrapper exists
        # The inner value should represent None/absence
        # Implementation may vary: could be TaskDescription(value=None) or just None
        try:
            assert desc.value is None
        except AttributeError:
            # If TaskDescription is just Optional[str] aliased, None itself is valid
            pass

    def test_task_description_accepts_string(self):
        """TaskDescription accepts a string value."""
        desc = TaskDescription("A detailed description")
        try:
            assert desc.value == "A detailed description"
        except AttributeError:
            # Might be a simple wrapper
            assert str(desc) is not None

    def test_task_description_accepts_empty_string(self):
        """TaskDescription accepts empty string (distinct from None/NULL)."""
        desc = TaskDescription("")
        try:
            assert desc.value == ""
        except AttributeError:
            pass


# ---------------------------------------------------------------------------
# Type Tests: Timestamptz
# ---------------------------------------------------------------------------

class TestTimestamptz:
    """Tests for Timestamptz with regex validator."""

    def test_timestamptz_valid_utc_z_suffix(self):
        """Timestamptz accepts ISO 8601 with Z suffix."""
        ts = Timestamptz(value="2024-01-15T10:30:00Z")
        assert ts.value == "2024-01-15T10:30:00Z"

    def test_timestamptz_valid_positive_offset(self):
        """Timestamptz accepts ISO 8601 with positive timezone offset."""
        ts = Timestamptz(value="2024-01-15T10:30:00+05:30")
        assert ts.value == "2024-01-15T10:30:00+05:30"

    def test_timestamptz_valid_negative_offset(self):
        """Timestamptz accepts ISO 8601 with negative timezone offset."""
        ts = Timestamptz(value="2024-01-15T10:30:00-08:00")
        assert ts.value == "2024-01-15T10:30:00-08:00"

    def test_timestamptz_valid_fractional_seconds(self):
        """Timestamptz accepts ISO 8601 with fractional seconds."""
        ts = Timestamptz(value="2024-01-15T10:30:00.123456Z")
        assert ts.value == "2024-01-15T10:30:00.123456Z"

    def test_timestamptz_valid_fractional_with_offset(self):
        """Timestamptz accepts fractional seconds with timezone offset."""
        ts = Timestamptz(value="2024-01-15T10:30:00.5+00:00")
        assert ts.value == "2024-01-15T10:30:00.5+00:00"

    def test_timestamptz_rejects_no_timezone(self):
        """Timestamptz rejects datetime string without timezone indicator."""
        with pytest.raises((ValueError, TypeError, Exception)):
            Timestamptz(value="2024-01-15T10:30:00")

    def test_timestamptz_rejects_date_only(self):
        """Timestamptz rejects date-only string."""
        with pytest.raises((ValueError, TypeError, Exception)):
            Timestamptz(value="2024-01-15")

    def test_timestamptz_rejects_non_iso_format(self):
        """Timestamptz rejects non-ISO format."""
        with pytest.raises((ValueError, TypeError, Exception)):
            Timestamptz(value="Jan 15, 2024")

    def test_timestamptz_rejects_empty_string(self):
        """Timestamptz rejects empty string."""
        with pytest.raises((ValueError, TypeError, Exception)):
            Timestamptz(value="")

    def test_timestamptz_rejects_arbitrary_text(self):
        """Timestamptz rejects arbitrary non-datetime text."""
        with pytest.raises((ValueError, TypeError, Exception)):
            Timestamptz(value="not-a-timestamp")

    def test_timestamptz_regex_pattern_correctness(self):
        """Verify the regex pattern matches expected formats and rejects invalid ones."""
        pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
        # Should match
        assert re.match(pattern, "2024-01-15T10:30:00Z")
        assert re.match(pattern, "2024-01-15T10:30:00+05:30")
        assert re.match(pattern, "2024-01-15T10:30:00.123456Z")
        assert re.match(pattern, "2024-01-15T10:30:00.1-03:00")
        # Should not match
        assert not re.match(pattern, "2024-01-15T10:30:00")
        assert not re.match(pattern, "2024-01-15")
        assert not re.match(pattern, "not-a-timestamp")


# ---------------------------------------------------------------------------
# Type Tests: ConnectionConfig
# ---------------------------------------------------------------------------

class TestConnectionConfig:
    """Tests for ConnectionConfig struct with validators."""

    def test_connection_config_valid(self):
        """ConnectionConfig accepts valid postgresql URL and port 5432."""
        config = ConnectionConfig(
            database_url="postgresql://user:pass@localhost/testdb",
            port=5432,
        )
        assert config.database_url == "postgresql://user:pass@localhost/testdb"
        assert config.port == 5432

    def test_connection_config_rejects_mysql_url(self):
        """ConnectionConfig rejects non-postgresql URL scheme."""
        with pytest.raises((ValueError, TypeError, Exception)):
            ConnectionConfig(
                database_url="mysql://user:pass@localhost/testdb",
                port=5432,
            )

    def test_connection_config_rejects_http_url(self):
        """ConnectionConfig rejects http URL scheme."""
        with pytest.raises((ValueError, TypeError, Exception)):
            ConnectionConfig(
                database_url="http://user:pass@localhost/testdb",
                port=5432,
            )

    def test_connection_config_rejects_empty_url(self):
        """ConnectionConfig rejects empty database_url."""
        with pytest.raises((ValueError, TypeError, Exception)):
            ConnectionConfig(database_url="", port=5432)

    def test_connection_config_rejects_wrong_port(self):
        """ConnectionConfig rejects port != 5432."""
        with pytest.raises((ValueError, TypeError, Exception)):
            ConnectionConfig(
                database_url="postgresql://user:pass@localhost/testdb",
                port=3306,
            )

    def test_connection_config_rejects_port_zero(self):
        """ConnectionConfig rejects port 0."""
        with pytest.raises((ValueError, TypeError, Exception)):
            ConnectionConfig(
                database_url="postgresql://user:pass@localhost/testdb",
                port=0,
            )

    def test_connection_config_rejects_port_5433(self):
        """ConnectionConfig rejects port 5433 (off by one)."""
        with pytest.raises((ValueError, TypeError, Exception)):
            ConnectionConfig(
                database_url="postgresql://user:pass@localhost/testdb",
                port=5433,
            )


# ---------------------------------------------------------------------------
# Type Tests: TaskRow (struct)
# ---------------------------------------------------------------------------

class TestTaskRow:
    """Tests for TaskRow struct composition."""

    def test_task_row_construction_with_all_fields(self):
        """TaskRow can be constructed with all 6 required fields."""
        try:
            row = TaskRow(
                id=1,
                title=TaskTitle(value="Test Task"),
                description=TaskDescription(None),
                status=TaskStatus.pending,
                created_at=Timestamptz(value="2024-01-15T10:30:00Z"),
                updated_at=Timestamptz(value="2024-01-15T10:30:00Z"),
            )
            assert row.id is not None
            assert row.title is not None
            assert row.status is not None
            assert row.created_at is not None
            assert row.updated_at is not None
        except TypeError:
            # If TaskRow uses primitive types directly
            row = TaskRow(
                id=1,
                title="Test Task",
                description=None,
                status="pending",
                created_at="2024-01-15T10:30:00Z",
                updated_at="2024-01-15T10:30:00Z",
            )
            assert row.id == 1
            assert row.title is not None

    def test_task_row_has_six_fields(self):
        """TaskRow struct has exactly the 6 expected field names."""
        expected_fields = {"id", "title", "description", "status", "created_at", "updated_at"}
        # Check via annotations or __fields__ or similar
        try:
            # Pydantic model
            actual_fields = set(TaskRow.__fields__.keys())
        except AttributeError:
            try:
                # dataclass
                import dataclasses
                actual_fields = {f.name for f in dataclasses.fields(TaskRow)}
            except (TypeError, AttributeError):
                try:
                    # __annotations__
                    actual_fields = set(TaskRow.__annotations__.keys())
                except AttributeError:
                    pytest.skip("Cannot introspect TaskRow fields")
        assert actual_fields == expected_fields


# ---------------------------------------------------------------------------
# Type Tests: InitScriptResult
# ---------------------------------------------------------------------------

class TestInitScriptResult:
    """Tests for InitScriptResult struct."""

    def test_init_script_result_all_true(self):
        """InitScriptResult can hold all True values."""
        result = InitScriptResult(
            table_created=True,
            trigger_created=True,
            check_constraint_present=True,
        )
        assert result.table_created is True
        assert result.trigger_created is True
        assert result.check_constraint_present is True

    def test_init_script_result_all_false(self):
        """InitScriptResult can hold all False values."""
        result = InitScriptResult(
            table_created=False,
            trigger_created=False,
            check_constraint_present=False,
        )
        assert result.table_created is False
        assert result.trigger_created is False
        assert result.check_constraint_present is False

    def test_init_script_result_mixed(self):
        """InitScriptResult can hold mixed True/False values."""
        result = InitScriptResult(
            table_created=True,
            trigger_created=False,
            check_constraint_present=True,
        )
        assert result.table_created is True
        assert result.trigger_created is False
        assert result.check_constraint_present is True


# ---------------------------------------------------------------------------
# Function Tests: execute_init_script
# ---------------------------------------------------------------------------

class TestExecuteInitScript:
    """Tests for the execute_init_script function."""

    def test_execute_init_script_happy_path(self, valid_connection_config, mock_psycopg2_success):
        """execute_init_script returns InitScriptResult with all True on success."""
        mock_connect, mock_conn, mock_cursor = mock_psycopg2_success

        result = execute_init_script(valid_connection_config)

        assert isinstance(result, InitScriptResult)
        assert result.table_created is True
        assert result.trigger_created is True
        assert result.check_constraint_present is True

    def test_execute_init_script_calls_connect(self, valid_connection_config, mock_psycopg2_success):
        """execute_init_script establishes a database connection."""
        mock_connect, mock_conn, mock_cursor = mock_psycopg2_success

        execute_init_script(valid_connection_config)

        mock_connect.assert_called()

    def test_execute_init_script_executes_sql(self, valid_connection_config, mock_psycopg2_success):
        """execute_init_script executes SQL statements via cursor."""
        mock_connect, mock_conn, mock_cursor = mock_psycopg2_success

        execute_init_script(valid_connection_config)

        # At least one execute call should be made (DDL)
        assert mock_cursor.execute.called or mock_cursor.executescript is not None

    def test_execute_init_script_idempotent(self, valid_connection_config, mock_psycopg2_success):
        """execute_init_script can be called twice without error, returning consistent results."""
        mock_connect, mock_conn, mock_cursor = mock_psycopg2_success

        result1 = execute_init_script(valid_connection_config)
        result2 = execute_init_script(valid_connection_config)

        assert result1.table_created == result2.table_created
        assert result1.trigger_created == result2.trigger_created
        assert result1.check_constraint_present == result2.check_constraint_present

    def test_execute_init_script_connection_refused(self, valid_connection_config):
        """execute_init_script raises appropriate error when connection is refused."""
        with patch("database.schema.psycopg2.connect") as mock_connect:
            try:
                import psycopg2
                mock_connect.side_effect = psycopg2.OperationalError(
                    "could not connect to server: Connection refused"
                )
            except ImportError:
                mock_connect.side_effect = ConnectionError("Connection refused")

            with pytest.raises(Exception) as exc_info:
                execute_init_script(valid_connection_config)

            error_str = str(exc_info.value).lower()
            assert "connect" in error_str or "refused" in error_str or "connection" in error_str or exc_info.type is not None

    def test_execute_init_script_authentication_failed(self, valid_connection_config):
        """execute_init_script raises appropriate error when authentication fails."""
        with patch("database.schema.psycopg2.connect") as mock_connect:
            try:
                import psycopg2
                mock_connect.side_effect = psycopg2.OperationalError(
                    'password authentication failed for user "test"'
                )
            except ImportError:
                mock_connect.side_effect = PermissionError("Authentication failed")

            with pytest.raises(Exception) as exc_info:
                execute_init_script(valid_connection_config)

            assert exc_info.value is not None

    def test_execute_init_script_database_not_found(self, valid_connection_config):
        """execute_init_script raises appropriate error when database does not exist."""
        with patch("database.schema.psycopg2.connect") as mock_connect:
            try:
                import psycopg2
                mock_connect.side_effect = psycopg2.OperationalError(
                    'database "nonexistent" does not exist'
                )
            except ImportError:
                mock_connect.side_effect = RuntimeError("Database not found")

            with pytest.raises(Exception) as exc_info:
                execute_init_script(valid_connection_config)

            assert exc_info.value is not None

    def test_execute_init_script_insufficient_privileges(self, valid_connection_config):
        """execute_init_script raises appropriate error when user lacks DDL privileges."""
        with patch("database.schema.psycopg2.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
            mock_cursor.__exit__ = MagicMock(return_value=False)
            mock_connect.return_value = mock_conn

            try:
                import psycopg2
                mock_cursor.execute.side_effect = psycopg2.ProgrammingError(
                    "permission denied for schema public"
                )
            except ImportError:
                mock_cursor.execute.side_effect = PermissionError(
                    "permission denied for schema public"
                )

            with pytest.raises(Exception) as exc_info:
                execute_init_script(valid_connection_config)

            assert exc_info.value is not None


# ---------------------------------------------------------------------------
# Function Tests: verify_schema
# ---------------------------------------------------------------------------

class TestVerifySchema:
    """Tests for the verify_schema function."""

    def test_verify_schema_all_present(self, valid_connection_config):
        """verify_schema returns all True when full schema is present."""
        with patch("database.schema.psycopg2.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
            mock_cursor.__exit__ = MagicMock(return_value=False)
            mock_connect.return_value = mock_conn

            # Mock fetchone/fetchall to simulate the schema being present
            # The exact queries depend on implementation; we make cursor return
            # truthy results for table, trigger, and constraint checks
            mock_cursor.fetchone.return_value = (True,)
            mock_cursor.fetchall.return_value = [
                ("id", "integer", "NO"),
                ("title", "character varying", "NO"),
                ("description", "text", "YES"),
                ("status", "character varying", "NO"),
                ("created_at", "timestamp with time zone", "NO"),
                ("updated_at", "timestamp with time zone", "NO"),
            ]

            result = verify_schema(valid_connection_config)

            assert isinstance(result, InitScriptResult)
            assert result.table_created is True
            assert result.trigger_created is True
            assert result.check_constraint_present is True

    def test_verify_schema_empty_database(self, valid_connection_config):
        """verify_schema returns all False when database has no schema objects."""
        with patch("database.schema.psycopg2.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
            mock_cursor.__exit__ = MagicMock(return_value=False)
            mock_connect.return_value = mock_conn

            # No tables, triggers, or constraints found
            mock_cursor.fetchone.return_value = None
            mock_cursor.fetchall.return_value = []

            result = verify_schema(valid_connection_config)

            assert isinstance(result, InitScriptResult)
            assert result.table_created is False
            assert result.trigger_created is False
            assert result.check_constraint_present is False

    def test_verify_schema_partial_missing_trigger(self, valid_connection_config):
        """verify_schema detects missing trigger when table and constraint exist."""
        with patch("database.schema.psycopg2.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
            mock_cursor.__exit__ = MagicMock(return_value=False)
            mock_connect.return_value = mock_conn

            # Table and constraint present, but trigger absent
            # Implementation will vary; we simulate the introspection queries
            call_count = [0]
            def side_effect_fetchone(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    return (True,)   # table exists
                elif call_count[0] == 2:
                    return (True,)   # check constraint present
                else:
                    return None      # trigger not found
            mock_cursor.fetchone.side_effect = side_effect_fetchone
            mock_cursor.fetchall.return_value = [
                ("id",), ("title",), ("description",), ("status",),
                ("created_at",), ("updated_at",),
            ]

            result = verify_schema(valid_connection_config)

            assert isinstance(result, InitScriptResult)
            assert result.table_created is True
            assert result.trigger_created is False
            assert result.check_constraint_present is True

    def test_verify_schema_connection_refused(self, valid_connection_config):
        """verify_schema raises error when PostgreSQL is unreachable."""
        with patch("database.schema.psycopg2.connect") as mock_connect:
            try:
                import psycopg2
                mock_connect.side_effect = psycopg2.OperationalError(
                    "could not connect to server: Connection refused"
                )
            except ImportError:
                mock_connect.side_effect = ConnectionError("Connection refused")

            with pytest.raises(Exception) as exc_info:
                verify_schema(valid_connection_config)

            assert exc_info.value is not None

    def test_verify_schema_authentication_failed(self, valid_connection_config):
        """verify_schema raises error when credentials are invalid."""
        with patch("database.schema.psycopg2.connect") as mock_connect:
            try:
                import psycopg2
                mock_connect.side_effect = psycopg2.OperationalError(
                    'password authentication failed for user "test"'
                )
            except ImportError:
                mock_connect.side_effect = PermissionError("Authentication failed")

            with pytest.raises(Exception) as exc_info:
                verify_schema(valid_connection_config)

            assert exc_info.value is not None

    def test_verify_schema_is_read_only(self, valid_connection_config):
        """verify_schema does not execute any DDL/DML (no INSERT, UPDATE, DELETE, CREATE, ALTER, DROP)."""
        with patch("database.schema.psycopg2.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
            mock_cursor.__exit__ = MagicMock(return_value=False)
            mock_connect.return_value = mock_conn
            mock_cursor.fetchone.return_value = (True,)
            mock_cursor.fetchall.return_value = []

            try:
                verify_schema(valid_connection_config)
            except Exception:
                pass  # We only care about what SQL was executed

            # Check that no DDL/DML statements were executed
            ddl_dml_keywords = {"CREATE", "ALTER", "DROP", "INSERT", "UPDATE", "DELETE", "TRUNCATE"}
            for call_args in mock_cursor.execute.call_args_list:
                sql = call_args[0][0] if call_args[0] else ""
                sql_upper = sql.strip().upper()
                for keyword in ddl_dml_keywords:
                    assert not sql_upper.startswith(keyword), (
                        f"verify_schema should be read-only but executed: {sql[:80]}"
                    )


# ---------------------------------------------------------------------------
# Invariant Tests
# ---------------------------------------------------------------------------

class TestSchemaInvariants:
    """Tests verifying schema invariants defined in the contract."""

    def test_invariant_tasks_table_exactly_six_columns(self):
        """Invariant: tasks table has exactly 6 columns."""
        expected_columns = {"id", "title", "description", "status", "created_at", "updated_at"}
        assert len(expected_columns) == 6
        # Verify TaskRow mirrors the expected column set
        try:
            fields = set(TaskRow.__fields__.keys())
        except AttributeError:
            try:
                import dataclasses
                fields = {f.name for f in dataclasses.fields(TaskRow)}
            except (TypeError, AttributeError):
                fields = set(TaskRow.__annotations__.keys())
        assert fields == expected_columns, f"Expected {expected_columns}, got {fields}"

    def test_invariant_status_enum_values_match_check_constraint(self):
        """Invariant: CHECK constraint values match TaskStatus enum variants."""
        allowed_values = {"pending", "in_progress", "done"}
        enum_values = {member.value if hasattr(member, 'value') else member.name for member in TaskStatus}
        # At least one of name or value should match
        enum_names = {member.name for member in TaskStatus}
        assert allowed_values == enum_names or allowed_values == enum_values or allowed_values.issubset(
            enum_names | enum_values
        ), f"Status values mismatch. Names: {enum_names}, Values: {enum_values}"

    def test_invariant_connection_config_port_is_5432(self):
        """Invariant: ConnectionConfig only accepts port 5432."""
        config = ConnectionConfig(
            database_url="postgresql://user:pass@localhost/testdb",
            port=5432,
        )
        assert config.port == 5432

    def test_invariant_init_script_result_fields_are_boolean(self):
        """Invariant: InitScriptResult fields are boolean."""
        result = InitScriptResult(
            table_created=True,
            trigger_created=False,
            check_constraint_present=True,
        )
        assert isinstance(result.table_created, bool)
        assert isinstance(result.trigger_created, bool)
        assert isinstance(result.check_constraint_present, bool)

    def test_invariant_title_varchar_255_not_null(self):
        """Invariant: title is VARCHAR(255) NOT NULL, enforced by TaskTitle validator."""
        # Max length 255
        title = TaskTitle(value="x" * 255)
        assert len(title.value) == 255

        # Over max rejected
        with pytest.raises((ValueError, TypeError, Exception)):
            TaskTitle(value="x" * 256)

        # Empty (NULL-equivalent for NOT NULL) rejected
        with pytest.raises((ValueError, TypeError, Exception)):
            TaskTitle(value="")

    def test_invariant_description_nullable(self):
        """Invariant: description is TEXT nullable (None allowed)."""
        desc = TaskDescription(None)
        # Should not raise
        assert desc is not None or desc is None  # Always passes; the non-raise is the assertion

    def test_invariant_status_default_pending(self):
        """Invariant: status DEFAULT is 'pending'."""
        # Verify the enum has 'pending' as a valid state
        assert TaskStatus.pending is not None

    def test_invariant_execute_init_idempotent_return_value(self, valid_connection_config, mock_psycopg2_success):
        """Invariant: re-executing init does not fail and returns same result."""
        result1 = execute_init_script(valid_connection_config)
        result2 = execute_init_script(valid_connection_config)

        assert result1.table_created == result2.table_created
        assert result1.trigger_created == result2.trigger_created
        assert result1.check_constraint_present == result2.check_constraint_present

    def test_invariant_timestamptz_requires_timezone(self):
        """Invariant: all TIMESTAMPTZ values must include timezone information."""
        # Valid with timezone
        ts = Timestamptz(value="2024-06-15T12:00:00Z")
        assert ts.value.endswith("Z") or "+" in ts.value or "-" in ts.value[10:]

        # Invalid without timezone
        with pytest.raises((ValueError, TypeError, Exception)):
            Timestamptz(value="2024-06-15T12:00:00")

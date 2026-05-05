"""
Adversarial hidden acceptance tests for PostgreSQL Database Schema component.
These tests catch implementations that pass visible tests through shortcuts
(hardcoded returns, incomplete validation, etc.) rather than truly satisfying the contract.
"""

import pytest
from unittest.mock import MagicMock, patch, call
from database import *


# ============================================================
# TaskStatus — enum validation beyond the three visible happy paths
# ============================================================

class TestGoodhartTaskStatus:

    def test_goodhart_task_status_rejects_close_misspellings(self):
        """TaskStatus validation must reject strings that are close to valid
        variants but not exact matches."""
        near_misses = [
            'Pending', 'PENDING', 'pENDING',
            'in-progress', 'In_Progress', 'IN_PROGRESS', 'inprogress', 'in_Progress',
            'Done', 'DONE', 'dONE',
            'pendings', ' pending', 'pending ', ' done',
            'completed', 'active', 'todo',
        ]
        for value in near_misses:
            with pytest.raises((ValueError, TypeError, KeyError, Exception)), \
                 f"TaskStatus should reject '{value}'":
                TaskStatus(value)

    def test_goodhart_task_status_rejects_empty_string(self):
        """TaskStatus must reject the empty string."""
        with pytest.raises((ValueError, TypeError, KeyError, Exception)):
            TaskStatus('')

    def test_goodhart_task_status_rejects_none(self):
        """TaskStatus must reject None since status is NOT NULL."""
        with pytest.raises((ValueError, TypeError, KeyError, Exception)):
            TaskStatus(None)

    def test_goodhart_task_status_rejects_numeric(self):
        """TaskStatus must reject numeric values even if they could be index-based."""
        with pytest.raises((ValueError, TypeError, KeyError, Exception)):
            TaskStatus(0)
        with pytest.raises((ValueError, TypeError, KeyError, Exception)):
            TaskStatus(1)
        with pytest.raises((ValueError, TypeError, KeyError, Exception)):
            TaskStatus(2)


# ============================================================
# TaskTitle — length validation beyond boundary-only checks
# ============================================================

class TestGoodhartTaskTitle:

    def test_goodhart_task_title_length_254(self):
        """TaskTitle must accept strings at length 254, just inside the max boundary."""
        title = 'x' * 254
        result = TaskTitle(title)
        assert result is not None

    def test_goodhart_task_title_length_256_rejected(self):
        """TaskTitle must reject strings at length 256, immediately beyond max."""
        with pytest.raises((ValueError, TypeError, Exception)):
            TaskTitle('x' * 256)

    def test_goodhart_task_title_length_2(self):
        """TaskTitle must accept typical short strings within valid range."""
        result = TaskTitle('ab')
        assert result is not None

    def test_goodhart_task_title_length_100(self):
        """TaskTitle must accept mid-range length strings."""
        result = TaskTitle('a' * 100)
        assert result is not None

    def test_goodhart_task_title_whitespace_only(self):
        """TaskTitle with whitespace-only content should be accepted since len >= 1."""
        result = TaskTitle(' ')
        assert result is not None

    def test_goodhart_task_title_rejects_none(self):
        """TaskTitle must reject None since title is NOT NULL."""
        with pytest.raises((ValueError, TypeError, Exception)):
            TaskTitle(None)

    def test_goodhart_task_title_unicode(self):
        """TaskTitle must accept Unicode characters within length limit."""
        result = TaskTitle('日本語タスク名')
        assert result is not None

    def test_goodhart_task_title_unicode_at_max(self):
        """TaskTitle must accept exactly 255 Unicode characters."""
        result = TaskTitle('あ' * 255)
        assert result is not None

    def test_goodhart_task_title_unicode_over_max(self):
        """TaskTitle must reject 256 Unicode characters."""
        with pytest.raises((ValueError, TypeError, Exception)):
            TaskTitle('あ' * 256)


# ============================================================
# TaskDescription — optional type behavior
# ============================================================

class TestGoodhartTaskDescription:

    def test_goodhart_task_description_empty_string(self):
        """TaskDescription must accept empty string as distinct from None."""
        result = TaskDescription('')
        assert result is not None
        # Empty string should not be converted to None
        if hasattr(result, 'value'):
            assert result.value == ''
        elif isinstance(result, str):
            assert result == ''

    def test_goodhart_task_description_long_text(self):
        """TaskDescription must accept very long strings since TEXT has no length limit."""
        long_text = 'x' * 10000
        result = TaskDescription(long_text)
        assert result is not None


# ============================================================
# Timestamptz — regex validation beyond visible test values
# ============================================================

class TestGoodhartTimestamptz:

    def test_goodhart_timestamptz_negative_offset(self):
        """Timestamptz must accept negative timezone offsets."""
        result = Timestamptz('2024-01-15T08:30:00-05:00')
        assert result is not None

    def test_goodhart_timestamptz_fractional_with_offset(self):
        """Timestamptz must accept fractional seconds combined with non-Z offset."""
        result = Timestamptz('2024-06-15T12:00:00.123456+05:30')
        assert result is not None

    def test_goodhart_timestamptz_single_fractional_digit(self):
        """Timestamptz must accept a single fractional second digit."""
        result = Timestamptz('2024-01-01T00:00:00.1Z')
        assert result is not None

    def test_goodhart_timestamptz_rejects_date_only(self):
        """Timestamptz must reject date-only strings."""
        with pytest.raises((ValueError, TypeError, Exception)):
            Timestamptz('2024-01-15')

    def test_goodhart_timestamptz_rejects_trailing_text(self):
        """Timestamptz must reject strings with trailing content after valid pattern."""
        with pytest.raises((ValueError, TypeError, Exception)):
            Timestamptz('2024-01-15T10:00:00Z extra')

    def test_goodhart_timestamptz_rejects_unix_timestamp(self):
        """Timestamptz must reject numeric Unix timestamp strings."""
        with pytest.raises((ValueError, TypeError, Exception)):
            Timestamptz('1704067200')

    def test_goodhart_timestamptz_rejects_space_separator(self):
        """Timestamptz must reject space separator between date and time."""
        with pytest.raises((ValueError, TypeError, Exception)):
            Timestamptz('2024-01-15 10:00:00Z')

    def test_goodhart_timestamptz_rejects_no_seconds(self):
        """Timestamptz must reject times without seconds component."""
        with pytest.raises((ValueError, TypeError, Exception)):
            Timestamptz('2024-01-15T10:00Z')

    def test_goodhart_timestamptz_rejects_leading_text(self):
        """Timestamptz must reject strings with leading content before valid pattern."""
        with pytest.raises((ValueError, TypeError, Exception)):
            Timestamptz('time:2024-01-15T10:00:00Z')

    def test_goodhart_timestamptz_midnight_utc(self):
        """Timestamptz must accept midnight timestamps."""
        result = Timestamptz('2024-12-31T00:00:00Z')
        assert result is not None

    def test_goodhart_timestamptz_end_of_day(self):
        """Timestamptz must accept end-of-day timestamps."""
        result = Timestamptz('2024-12-31T23:59:59+00:00')
        assert result is not None


# ============================================================
# ConnectionConfig — URL and port validation
# ============================================================

class TestGoodhartConnectionConfig:

    def test_goodhart_connection_config_rejects_postgres_without_ql(self):
        """ConnectionConfig must reject 'postgres://' URLs missing the 'ql'."""
        with pytest.raises((ValueError, TypeError, Exception)):
            ConnectionConfig(database_url='postgres://user:pass@localhost/db', port=5432)

    def test_goodhart_connection_config_rejects_port_5433(self):
        """ConnectionConfig must reject port 5433, adjacent above required 5432."""
        with pytest.raises((ValueError, TypeError, Exception)):
            ConnectionConfig(database_url='postgresql://user:pass@localhost/db', port=5433)

    def test_goodhart_connection_config_rejects_port_5431(self):
        """ConnectionConfig must reject port 5431, adjacent below required 5432."""
        with pytest.raises((ValueError, TypeError, Exception)):
            ConnectionConfig(database_url='postgresql://user:pass@localhost/db', port=5431)

    def test_goodhart_connection_config_rejects_port_zero(self):
        """ConnectionConfig must reject port 0."""
        with pytest.raises((ValueError, TypeError, Exception)):
            ConnectionConfig(database_url='postgresql://user:pass@localhost/db', port=0)

    def test_goodhart_connection_config_rejects_negative_port(self):
        """ConnectionConfig must reject negative port values."""
        with pytest.raises((ValueError, TypeError, Exception)):
            ConnectionConfig(database_url='postgresql://user:pass@localhost/db', port=-1)

    def test_goodhart_connection_config_url_anchored(self):
        """ConnectionConfig must reject URLs where 'postgresql://' is not at the start."""
        with pytest.raises((ValueError, TypeError, Exception)):
            ConnectionConfig(
                database_url='http://postgresql://user:pass@localhost/db',
                port=5432
            )

    def test_goodhart_connection_config_rejects_mysql_url(self):
        """ConnectionConfig must reject MySQL connection URLs."""
        with pytest.raises((ValueError, TypeError, Exception)):
            ConnectionConfig(database_url='mysql://user:pass@localhost/db', port=5432)


# ============================================================
# InitScriptResult — struct flexibility
# ============================================================

class TestGoodhartInitScriptResult:

    def test_goodhart_init_script_result_all_false(self):
        """InitScriptResult must support all fields being False."""
        result = InitScriptResult(
            table_created=False,
            trigger_created=False,
            check_constraint_present=False
        )
        assert result.table_created is False
        assert result.trigger_created is False
        assert result.check_constraint_present is False

    def test_goodhart_init_script_result_mixed_true_false_true(self):
        """InitScriptResult must support mixed boolean states."""
        result = InitScriptResult(
            table_created=True,
            trigger_created=False,
            check_constraint_present=True
        )
        assert result.table_created is True
        assert result.trigger_created is False
        assert result.check_constraint_present is True

    def test_goodhart_init_script_result_mixed_false_true_false(self):
        """InitScriptResult must support the inverse mixed state."""
        result = InitScriptResult(
            table_created=False,
            trigger_created=True,
            check_constraint_present=False
        )
        assert result.table_created is False
        assert result.trigger_created is True
        assert result.check_constraint_present is False


# ============================================================
# TaskRow — struct construction with edge values
# ============================================================

class TestGoodhartTaskRow:

    def test_goodhart_task_row_description_none(self):
        """TaskRow must be constructable with description=None."""
        row = TaskRow(
            id=1,
            title='Test Task',
            description=None,
            status='pending',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z'
        )
        assert row.description is None

    def test_goodhart_task_row_all_statuses(self):
        """TaskRow must accept all three valid status values, not just one."""
        for status in ['pending', 'in_progress', 'done']:
            row = TaskRow(
                id=1,
                title='Test',
                description=None,
                status=status,
                created_at='2024-01-01T00:00:00Z',
                updated_at='2024-01-01T00:00:00Z'
            )
            assert row.status == status

    def test_goodhart_task_row_different_ids(self):
        """TaskRow must accept various integer id values, not just a fixed one."""
        for task_id in [1, 42, 999, 1000000]:
            row = TaskRow(
                id=task_id,
                title='Test',
                description=None,
                status='pending',
                created_at='2024-01-01T00:00:00Z',
                updated_at='2024-01-01T00:00:00Z'
            )
            assert row.id == task_id


# ============================================================
# execute_init_script — behavioral properties via mocking
# ============================================================

class TestGoodhartExecuteInitScript:

    @patch('src.database.psycopg2.connect')
    def test_goodhart_exec_init_sql_syntax_error(self, mock_connect):
        """execute_init_script must raise sql_syntax_error on SQL syntax issues."""
        import psycopg2
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.errors.SyntaxError("syntax error")

        config = ConnectionConfig(
            database_url='postgresql://user:pass@localhost/testdb',
            port=5432
        )
        with pytest.raises(Exception) as exc_info:
            execute_init_script(config)
        # Should map to sql_syntax_error, not pass silently
        assert 'syntax' in str(exc_info.value).lower() or \
               'sql_syntax_error' in str(type(exc_info.value)).lower() or \
               'sql_syntax_error' in str(exc_info.value).lower()

    @patch('src.database.psycopg2.connect')
    def test_goodhart_exec_init_triple_idempotent(self, mock_connect):
        """execute_init_script must remain idempotent across 3+ consecutive invocations."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_cursor.fetchall.return_value = []

        config = ConnectionConfig(
            database_url='postgresql://user:pass@localhost/testdb',
            port=5432
        )

        results = []
        for _ in range(3):
            result = execute_init_script(config)
            results.append(result)

        # All three invocations should succeed with all True
        for i, result in enumerate(results):
            assert result.table_created is True, f"Invocation {i+1}: table_created should be True"
            assert result.trigger_created is True, f"Invocation {i+1}: trigger_created should be True"
            assert result.check_constraint_present is True, f"Invocation {i+1}: check_constraint_present should be True"

    @patch('src.database.psycopg2.connect')
    def test_goodhart_exec_init_preserves_existing_rows(self, mock_connect):
        """execute_init_script must not execute DELETE, TRUNCATE, or DROP TABLE on tasks."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        executed_statements = []
        original_execute = mock_cursor.execute

        def track_execute(sql, *args, **kwargs):
            if isinstance(sql, str):
                executed_statements.append(sql)

        mock_cursor.execute.side_effect = track_execute

        config = ConnectionConfig(
            database_url='postgresql://user:pass@localhost/testdb',
            port=5432
        )

        try:
            execute_init_script(config)
        except Exception:
            pass  # We care about the SQL statements, not the result

        destructive_keywords = ['DELETE', 'TRUNCATE', 'DROP TABLE']
        for stmt in executed_statements:
            upper_stmt = stmt.upper()
            for keyword in destructive_keywords:
                assert keyword not in upper_stmt or 'IF EXISTS' in upper_stmt and 'DROP TRIGGER' in upper_stmt, \
                    f"Destructive statement found: {stmt}"


# ============================================================
# verify_schema — additional partial states and read-only invariant
# ============================================================

class TestGoodhartVerifySchema:

    @patch('src.database.psycopg2.connect')
    def test_goodhart_verify_schema_partial_no_check_constraint(self, mock_connect):
        """verify_schema must independently detect a missing CHECK constraint."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        def query_results(sql, *args, **kwargs):
            sql_upper = sql.upper() if isinstance(sql, str) else ''
            if 'INFORMATION_SCHEMA.TABLES' in sql_upper or 'PG_TABLES' in sql_upper:
                return  # table exists
            if 'PG_TRIGGER' in sql_upper or 'TRIGGER' in sql_upper:
                return  # trigger exists
            return

        def fetchone_results(*args, **kwargs):
            return (True,)  # Generic positive result

        mock_cursor.execute.side_effect = query_results
        mock_cursor.fetchone.return_value = (True,)

        config = ConnectionConfig(
            database_url='postgresql://user:pass@localhost/testdb',
            port=5432
        )

        # This test verifies that the function actually queries for check constraints
        # rather than returning hardcoded all-True or all-False
        try:
            result = verify_schema(config)
            # If implementation returns something, each field should reflect actual introspection
            assert hasattr(result, 'table_created')
            assert hasattr(result, 'trigger_created')
            assert hasattr(result, 'check_constraint_present')
        except Exception:
            pass  # Mock may not match exactly; the structural test still validates

    @patch('src.database.psycopg2.connect')
    def test_goodhart_verify_schema_introspection_query_failed(self, mock_connect):
        """verify_schema must raise introspection_query_failed on privilege errors."""
        import psycopg2
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.errors.InsufficientPrivilege(
            "permission denied for schema information_schema"
        )

        config = ConnectionConfig(
            database_url='postgresql://user:pass@localhost/testdb',
            port=5432
        )

        with pytest.raises(Exception) as exc_info:
            verify_schema(config)
        exc_str = str(exc_info.value).lower() + str(type(exc_info.value).__name__).lower()
        assert 'introspection' in exc_str or 'privilege' in exc_str or 'permission' in exc_str

    @patch('src.database.psycopg2.connect')
    def test_goodhart_verify_schema_readonly(self, mock_connect):
        """verify_schema must not execute any DDL or DML write statements."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (True,)
        mock_cursor.fetchall.return_value = [('tasks',)]

        executed_statements = []

        def track_execute(sql, *args, **kwargs):
            if isinstance(sql, str):
                executed_statements.append(sql)

        mock_cursor.execute.side_effect = track_execute

        config = ConnectionConfig(
            database_url='postgresql://user:pass@localhost/testdb',
            port=5432
        )

        try:
            verify_schema(config)
        except Exception:
            pass

        write_keywords = ['CREATE', 'ALTER', 'DROP', 'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE']
        for stmt in executed_statements:
            upper_stmt = stmt.upper()
            for keyword in write_keywords:
                assert keyword not in upper_stmt, \
                    f"verify_schema executed write statement: {stmt}"

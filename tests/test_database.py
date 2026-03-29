"""Tests for SQL database integration."""

import pytest

from mdcomp.database import _sanitize_url, run_sql
from mdcomp.errors import DatabaseError
from mdcomp.render import render_string

# Use SQLite in-memory for all tests
SQLITE_URL = "sqlite:///:memory:"


class TestRunSql:
    """Tests for the run_sql function."""

    def test_returns_empty_for_ddl(self) -> None:
        """DDL statements return empty list."""
        # Note: in-memory SQLite creates a new database each time,
        # so this just tests that DDL doesn't crash
        result = run_sql(SQLITE_URL, "CREATE TABLE test (id INTEGER)")
        assert result == []

    def test_select_with_setup(self, tmp_path) -> None:
        """SELECT query with proper setup returns list of dicts."""
        db_file = tmp_path / "test.db"
        db_url = f"sqlite:///{db_file}"

        # Setup: create table and insert data
        run_sql(db_url, "CREATE TABLE users (id INTEGER, name TEXT, email TEXT)")
        run_sql(
            db_url,
            "INSERT INTO users VALUES (:id, :name, :email)",
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
        )
        run_sql(
            db_url,
            "INSERT INTO users VALUES (:id, :name, :email)",
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
        )

        # Test: query the data
        results = run_sql(db_url, "SELECT name, email FROM users ORDER BY id")

        assert len(results) == 2
        assert results[0] == {"name": "Alice", "email": "alice@example.com"}
        assert results[1] == {"name": "Bob", "email": "bob@example.com"}

    def test_parameterized_query_named(self, tmp_path) -> None:
        """Named parameter binding works correctly."""
        db_file = tmp_path / "test.db"
        db_url = f"sqlite:///{db_file}"

        run_sql(db_url, "CREATE TABLE items (id INTEGER, status TEXT)")
        run_sql(db_url, "INSERT INTO items VALUES (1, 'active')")
        run_sql(db_url, "INSERT INTO items VALUES (2, 'inactive')")
        run_sql(db_url, "INSERT INTO items VALUES (3, 'active')")

        results = run_sql(
            db_url,
            "SELECT id FROM items WHERE status = :status ORDER BY id",
            {"status": "active"},
        )

        assert len(results) == 2
        assert results[0]["id"] == 1
        assert results[1]["id"] == 3

    def test_multiple_named_params(self, tmp_path) -> None:
        """Multiple named parameters work correctly."""
        db_file = tmp_path / "test.db"
        db_url = f"sqlite:///{db_file}"

        run_sql(db_url, "CREATE TABLE items (id INTEGER, status TEXT, category TEXT)")
        run_sql(db_url, "INSERT INTO items VALUES (1, 'active', 'A')")
        run_sql(db_url, "INSERT INTO items VALUES (2, 'inactive', 'A')")
        run_sql(db_url, "INSERT INTO items VALUES (3, 'active', 'B')")

        results = run_sql(
            db_url,
            "SELECT id FROM items WHERE status = :status AND category = :cat ORDER BY id",
            {"status": "active", "cat": "A"},
        )

        assert len(results) == 1
        assert results[0]["id"] == 1

    def test_empty_result(self, tmp_path) -> None:
        """Empty result returns empty list."""
        db_file = tmp_path / "test.db"
        db_url = f"sqlite:///{db_file}"

        run_sql(db_url, "CREATE TABLE items (id INTEGER)")

        results = run_sql(db_url, "SELECT * FROM items")

        assert results == []

    def test_null_values(self, tmp_path) -> None:
        """NULL values are handled correctly."""
        db_file = tmp_path / "test.db"
        db_url = f"sqlite:///{db_file}"

        run_sql(db_url, "CREATE TABLE items (id INTEGER, value TEXT)")
        run_sql(db_url, "INSERT INTO items VALUES (1, NULL)")

        results = run_sql(db_url, "SELECT * FROM items")

        assert len(results) == 1
        assert results[0]["id"] == 1
        assert results[0]["value"] is None

    def test_invalid_query_raises_error(self, tmp_path) -> None:
        """Invalid SQL raises DatabaseError."""
        db_file = tmp_path / "test.db"
        db_url = f"sqlite:///{db_file}"

        with pytest.raises(DatabaseError, match="Query failed"):
            run_sql(db_url, "SELECT * FROM nonexistent_table")

    def test_invalid_connection_raises_error(self) -> None:
        """Invalid connection URL raises DatabaseError."""
        with pytest.raises(DatabaseError, match="Failed to connect"):
            run_sql("invalid://not-a-real-url", "SELECT 1")

    def test_unicode_data(self, tmp_path) -> None:
        """Unicode characters in data are handled correctly."""
        db_file = tmp_path / "test.db"
        db_url = f"sqlite:///{db_file}"

        run_sql(db_url, "CREATE TABLE items (name TEXT)")
        run_sql(db_url, "INSERT INTO items VALUES (:name)", {"name": "日本語テスト"})
        run_sql(db_url, "INSERT INTO items VALUES (:name)", {"name": "emoji 🎉"})

        results = run_sql(db_url, "SELECT name FROM items ORDER BY name")

        assert len(results) == 2
        assert results[0]["name"] == "emoji 🎉"
        assert results[1]["name"] == "日本語テスト"

    def test_engine_caching(self, tmp_path) -> None:
        """Engines are cached to avoid connection pool exhaustion."""
        from mdcomp.database import _engine_cache

        db_file = tmp_path / "test.db"
        db_url = f"sqlite:///{db_file}"

        # Clear cache for this test
        _engine_cache.clear()

        run_sql(db_url, "CREATE TABLE test (id INTEGER)")
        run_sql(db_url, "SELECT 1")
        run_sql(db_url, "SELECT 2")

        # Should only have one engine for this URL
        assert db_url in _engine_cache
        assert len([k for k in _engine_cache if db_file.name in k]) == 1


class TestUrlSanitization:
    """Tests for URL sanitization (credential hiding)."""

    def test_sanitize_url_with_password(self) -> None:
        """Passwords are replaced with asterisks."""
        url = "postgresql://admin:supersecret@db.example.com/mydb"
        sanitized = _sanitize_url(url)
        assert "supersecret" not in sanitized
        assert "****" in sanitized
        assert "admin" in sanitized
        assert "db.example.com" in sanitized

    def test_sanitize_url_with_port(self) -> None:
        """URLs with ports are handled correctly."""
        url = "mysql://user:pass@localhost:3306/db"
        sanitized = _sanitize_url(url)
        assert "pass" not in sanitized
        assert "3306" in sanitized

    def test_sanitize_url_without_password(self) -> None:
        """URLs without passwords are unchanged."""
        url = "sqlite:///test.db"
        assert _sanitize_url(url) == url

    def test_sanitize_invalid_url(self) -> None:
        """Invalid URLs return generic placeholder."""
        # This shouldn't happen in practice, but we handle it gracefully
        result = _sanitize_url("not a url at all :::")
        assert result in ["not a url at all :::", "<database url>"]


class TestSqlInTemplates:
    """Integration tests for sql() function in templates."""

    def test_sql_in_template(self, tmp_path) -> None:
        """sql() function works in Jinja2 templates."""
        db_file = tmp_path / "test.db"
        db_url = f"sqlite:///{db_file}"

        # Setup database
        run_sql(db_url, "CREATE TABLE users (name TEXT)")
        run_sql(db_url, "INSERT INTO users VALUES (:name)", {"name": "Alice"})
        run_sql(db_url, "INSERT INTO users VALUES (:name)", {"name": "Bob"})

        # Render template with sql()
        template = """Users:
{% for user in sql("SELECT name FROM users ORDER BY name") %}
- {{ user.name }}
{% endfor %}"""

        result = render_string(template, {"db_url": db_url})

        assert "- Alice" in result
        assert "- Bob" in result

    def test_sql_with_params_in_template(self, tmp_path) -> None:
        """sql() with parameters works in templates."""
        db_file = tmp_path / "test.db"
        db_url = f"sqlite:///{db_file}"

        run_sql(db_url, "CREATE TABLE items (name TEXT, category TEXT)")
        run_sql(db_url, "INSERT INTO items VALUES ('Apple', 'fruit')")
        run_sql(db_url, "INSERT INTO items VALUES ('Carrot', 'vegetable')")

        template = """Fruits:
{% for item in sql("SELECT name FROM items WHERE category = :cat", {"cat": "fruit"}) %}
- {{ item.name }}
{% endfor %}"""

        result = render_string(template, {"db_url": db_url})

        assert "- Apple" in result
        assert "Carrot" not in result

    def test_sql_without_db_url_raises_error(self) -> None:
        """sql() without db_url raises clear error."""
        template = "{% for x in sql('SELECT 1') %}{{ x }}{% endfor %}"

        with pytest.raises(DatabaseError, match="sql\\(\\) requires a database URL"):
            render_string(template, {})

    def test_db_url_from_context(self, tmp_path) -> None:
        """db_url can be provided via context."""
        db_file = tmp_path / "test.db"
        db_url = f"sqlite:///{db_file}"

        run_sql(db_url, "CREATE TABLE test (val INTEGER)")
        run_sql(db_url, "INSERT INTO test VALUES (42)")

        template = "{{ sql('SELECT val FROM test')[0].val }}"
        result = render_string(template, {"db_url": db_url})

        assert result == "42"

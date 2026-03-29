"""SQL database integration for templates."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse, urlunparse

from mdcomp.errors import DatabaseError

if TYPE_CHECKING:
    from sqlalchemy import Engine

# Cache engines by URL to avoid connection pool exhaustion
_engine_cache: dict[str, Engine] = {}


def _sanitize_url(url: str) -> str:
    """Remove password from database URL for safe logging."""
    try:
        parsed = urlparse(url)
        if parsed.password:
            # Replace password with asterisks
            if parsed.port:
                netloc = f"{parsed.username}:****@{parsed.hostname}:{parsed.port}"
            else:
                netloc = f"{parsed.username}:****@{parsed.hostname}"
            return urlunparse(parsed._replace(netloc=netloc))
        return url
    except Exception:
        # If URL parsing fails, just return a generic message
        return "<database url>"


def _get_engine(db_url: str) -> Engine:
    """Get or create a cached SQLAlchemy engine for the given URL."""
    try:
        from sqlalchemy import create_engine
    except ImportError:
        raise DatabaseError(
            "sqlalchemy is not installed. Install with: pip install mdcomp[sql]"
        ) from None

    if db_url not in _engine_cache:
        try:
            _engine_cache[db_url] = create_engine(db_url)
        except Exception as e:
            safe_url = _sanitize_url(db_url)
            raise DatabaseError(f"Failed to connect to {safe_url}: {type(e).__name__}") from e

    return _engine_cache[db_url]


def run_sql(
    db_url: str,
    query: str,
    params: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Execute a SQL query and return results as a list of dicts.

    Args:
        db_url: SQLAlchemy connection URL (e.g., "sqlite:///db.sqlite",
                "mysql+pymysql://user:pass@host/db",
                "postgresql://user:pass@host/db")
        query: SQL query string with named parameter placeholders using :name syntax.
               Example: "SELECT * FROM users WHERE status = :status"
        params: Query parameters as dict mapping names to values.
                Example: {"status": "active"}

    Returns:
        List of dicts where keys are column names

    Raises:
        DatabaseError: If sqlalchemy is not installed, connection fails,
                      or query execution fails
    """
    try:
        from sqlalchemy import text
        from sqlalchemy.exc import SQLAlchemyError
    except ImportError:
        raise DatabaseError(
            "sqlalchemy is not installed. Install with: pip install mdcomp[sql]"
        ) from None

    engine = _get_engine(db_url)
    safe_url = _sanitize_url(db_url)

    try:
        with engine.connect() as conn:
            if params is None:
                result = conn.execute(text(query))
            else:
                result = conn.execute(text(query), params)

            # Check if this is a SELECT query that returns rows
            if result.returns_rows:
                rows = result.mappings().all()
                return [dict(row) for row in rows]

            # For INSERT/UPDATE/DELETE/DDL, commit and return empty list
            conn.commit()
            return []

    except SQLAlchemyError as e:
        raise DatabaseError(f"Query failed on {safe_url}: {type(e).__name__}") from e
    except Exception as e:
        raise DatabaseError(f"Database error on {safe_url}: {type(e).__name__}") from e

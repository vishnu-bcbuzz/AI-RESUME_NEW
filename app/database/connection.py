"""Neon PostgreSQL Connection Lifecycle & Pool Management for FUTRSEC."""

import logging
import time
from contextlib import contextmanager
from typing import Generator, Dict, Any, Optional
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import settings

logger = logging.getLogger("futrsec.database")


class DatabaseManager:
    """Manages the database connection pool with lifecycle methods and health checks."""

    def __init__(self, database_url: str):
        self._database_url = database_url
        self._pool: Optional[ConnectionPool] = None

    def initialize(self) -> None:
        """Initializes the connection pool on application startup."""
        if self._pool is None:
            logger.info("Initializing Neon PostgreSQL connection pool...")
            # min_size, max_size, and timeout
            self._pool = ConnectionPool(
                conninfo=self._database_url,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                timeout=settings.DB_CONNECT_TIMEOUT_SEC,
                open=True,
                check=ConnectionPool.check_connection,
                max_idle=120.0,
                max_lifetime=1800.0,
                kwargs={"row_factory": dict_row},
            )
            logger.info("Database connection pool initialized successfully with active health checks.")

    def close(self) -> None:
        """Closes the connection pool on application shutdown."""
        if self._pool is not None:
            logger.info("Closing Neon PostgreSQL connection pool...")
            self._pool.close()
            self._pool = None
            logger.info("Connection pool closed.")

    @contextmanager
    def get_connection(self) -> Generator[psycopg.Connection, None, None]:
        """Context manager yielding a pooled connection with health verification."""
        if self._pool is None:
            self.initialize()

        assert self._pool is not None

        with self._pool.connection() as conn:
            yield conn

    def check_health(self) -> Dict[str, Any]:
        """Performs a read-only health check query against Neon PostgreSQL."""
        start_time = time.perf_counter()
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 AS alive, current_database() AS db_name;")
                    result = cur.fetchone()
                    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    return {
                        "status": "healthy",
                        "database": result["db_name"] if result else "unknown",
                        "latency_ms": latency_ms,
                    }
        except Exception as exc:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error("Database health check failed: %s", type(exc).__name__)
            return {
                "status": "unhealthy",
                "error": type(exc).__name__,
                "latency_ms": latency_ms,
            }


db_manager = DatabaseManager(settings.DATABASE_URL)

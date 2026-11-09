"""
TenderFit - Database Connection and Session Management
Configured for PostgreSQL with automatic fallback to SQLite for immediate local development.
"""

import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import OperationalError

from config.settings import settings

logger = logging.getLogger("tenderfit.database")
logging.basicConfig(level=logging.INFO)

Base = declarative_base()


import socket
from urllib.parse import urlparse

def is_db_port_open(url: str, timeout_sec: float = 0.5) -> bool:
    """Fast socket check to see if database host and port are accepting connections."""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        with socket.create_connection((host, port), timeout=timeout_sec):
            return True
    except Exception:
        return False


def get_engine():
    """
    Creates an SQLAlchemy engine.
    Attempts to connect to PostgreSQL first.
    If PostgreSQL is unreachable, falls back to SQLite so the application works seamlessly.
    """
    target_url = settings.DATABASE_URL
    if target_url.startswith("postgresql://"):
        target_url = target_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    is_postgres = target_url.startswith("postgresql")

    if is_postgres:
        if not is_db_port_open(target_url, timeout_sec=0.5):
            logger.info(
                f"[DATABASE NOTICE] PostgreSQL service is not running on port 5432.\n"
                f"Activating zero-friction local SQLite database ({settings.SQLITE_FALLBACK_URL}).\n"
                f"When PostgreSQL is started, TenderFit will connect to it automatically.\n"
            )
            fallback_engine = create_engine(
                settings.SQLITE_FALLBACK_URL,
                connect_args={"check_same_thread": False},
            )
            return fallback_engine, "sqlite"

        try:
            logger.info(f"Connecting to PostgreSQL at {target_url}...")
            engine = create_engine(
                target_url,
                pool_pre_ping=True,
                connect_args={"connect_timeout": 2},
            )
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to PostgreSQL database.")
            return engine, "postgresql"
        except Exception as e:
            logger.warning(
                f"[DATABASE NOTICE] Error connecting to PostgreSQL ({e}). Falling back to SQLite."
            )
            fallback_engine = create_engine(
                settings.SQLITE_FALLBACK_URL,
                connect_args={"check_same_thread": False},
            )
            return fallback_engine, "sqlite"
    else:
        # User explicitly configured SQLite or another DB
        fallback_engine = create_engine(
            target_url,
            connect_args={"check_same_thread": False} if "sqlite" in target_url else {},
        )
        return fallback_engine, "sqlite"


engine, ACTIVE_DIALECT = get_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a transactional database session per request.
    Closes the session when request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all registered database tables."""
    # Import all models before create_all to ensure they are registered with Base metadata
    import backend.models.company  # noqa: F401
    import backend.models.tender   # noqa: F401
    import backend.models.log      # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info(f"Initialized database tables successfully using dialect '{ACTIVE_DIALECT}'.")


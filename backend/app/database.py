"""
Database engine, session factory, and base model setup.
Supports both SQLite (development) and PostgreSQL (production).
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# ─── Engine Configuration ────────────────────────────────────────────────────

def get_engine():
    """Create SQLAlchemy engine based on DATABASE_URL."""
    db_url = settings.DATABASE_URL

    if db_url.startswith("sqlite"):
        # SQLite: use StaticPool for testing compatibility
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=settings.DEBUG,
        )
        # Enable foreign key enforcement for SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    else:
        # PostgreSQL / other relational DBs
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=settings.DEBUG,
        )

    return engine


engine = get_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


# ─── Dependency ───────────────────────────────────────────────────────────────

def get_db():
    """
    FastAPI dependency that yields a database session and
    guarantees it is closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

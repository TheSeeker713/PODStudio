"""
Database Setup - SQLite + SQLModel
Schema: Asset, Pack, Job

STEP 4: Database engine creation and table initialization
"""

from pathlib import Path

from sqlmodel import SQLModel, create_engine

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Global engine instance
_engine = None


def reset_engine():
    """Reset global engine (for testing only)"""
    global _engine
    _engine = None


def get_engine():
    """
    Get or create SQLModel engine

    Returns:
        Engine instance for database operations
    """
    global _engine
    if _engine is None:
        db_path = Path(settings.db_path)
        db_url = f"sqlite:///{db_path}"

        # Ensure parent directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        _engine = create_engine(
            db_url,
            echo=settings.app_debug,  # Log SQL in debug mode
            connect_args={"check_same_thread": False},  # Required for SQLite
        )
        logger.info(f"Database engine created: {db_path}")

    return _engine


def create_db_and_tables():
    """
    Create database file and all tables

    Called on application startup to ensure schema exists.
    Safe to call multiple times (idempotent).
    """
    engine = get_engine()

    # Import models to ensure they're registered with SQLModel
    from app.backend.models import entities  # noqa: F401

    # Create all tables
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created/verified")


# Backwards compatibility
engine = get_engine()

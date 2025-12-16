"""
MySQL Database Connection
=========================

SQLAlchemy database connection and session management.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

from ..config import settings

# Create engine with connection pooling
engine = create_engine(
    settings.mysql_dsn,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.app_debug,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Get database session.
    
    Yields:
        Session: SQLAlchemy session
    
    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Get database session as context manager.
    
    Usage:
        with get_db_context() as db:
            db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    # Import all models to ensure they are registered
    from ..models import (  # noqa: F401
        Project, Document, Asset, DamageScenario,
        ThreatRisk, AttackPath, ControlMeasure, Report
    )
    from ..models.base import Base as ModelBase
    
    # Create all tables
    ModelBase.metadata.create_all(bind=engine)


# Connection event listeners for debugging
@event.listens_for(engine, "connect")
def set_search_path(dbapi_connection, connection_record):
    """Set connection options on connect."""
    pass


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Handle connection checkout from pool."""
    pass

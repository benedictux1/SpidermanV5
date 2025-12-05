"""
Database Manager
Context manager for database sessions
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
import os
import logging

logger = logging.getLogger(__name__)

# Base class for all models
Base = declarative_base()

# Global engine and session factory
_engine = None
_SessionLocal = None


def get_database_url():
    """Get database URL from environment or default to SQLite"""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Render.com provides postgres:// but SQLAlchemy needs postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url
    else:
        # Development: use SQLite
        return 'sqlite:///kith_platform.db'


def get_engine():
    """Get or create database engine"""
    global _engine
    if _engine is None:
        database_url = get_database_url()
        _engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=False  # Set to True for SQL query logging
        )
        logger.info(f"Database engine created: {database_url.split('@')[-1] if '@' in database_url else database_url}")
    return _engine


def get_session_factory():
    """Get or create session factory"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
    return _SessionLocal


class DatabaseManager:
    """Database manager with context manager support"""
    
    def __init__(self):
        self.engine = get_engine()
        self.SessionLocal = get_session_factory()
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}", exc_info=True)
            raise
        finally:
            session.close()
    
    def create_all_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")


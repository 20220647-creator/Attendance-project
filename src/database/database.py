"""
Database manager using Singleton Pattern
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator

from src.models.models import Base
from src.config.config import config


class DatabaseManager:
    """Singleton Database Manager"""
    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialize_database()
        self._initialized = True

    def _initialize_database(self):
        """Initialize database connection and create tables"""
        # For SQLite, use StaticPool to avoid threading issues
        if config.DATABASE_URL.startswith('sqlite'):
            self._engine = create_engine(
                config.DATABASE_URL,
                connect_args={'check_same_thread': False},
                poolclass=StaticPool
            )
        else:
            self._engine = create_engine(config.DATABASE_URL)

        # Create session factory
        self._session_factory = sessionmaker(bind=self._engine)

        # Create all tables
        Base.metadata.create_all(self._engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions
        Usage:
            with db_manager.get_session() as session:
                # do something with session
        """
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(self._engine)

    def drop_tables(self):
        """Drop all tables from the database"""
        Base.metadata.drop_all(self._engine)


# Global database manager instance
db_manager = DatabaseManager()


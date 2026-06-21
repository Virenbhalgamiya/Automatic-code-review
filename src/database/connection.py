import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from src.config import settings

logger = logging.getLogger("database")

class DatabaseError(Exception):
    """Base exception for all database-related operations."""
    pass

class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails or cannot be established."""
    pass

# Create Engine and SessionMaker
# pool_pre_ping=True ensures we verify connection viability before checking it out
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

def init_db() -> None:
    """Creates all required tables in PostgreSQL on startup."""
    from src.database.models import Base
    try:
        Base.metadata.create_all(bind=engine)
    except (OperationalError, SQLAlchemyError) as e:
        logger.error(f"Failed to initialize database tables: {str(e)}")
        raise DatabaseConnectionError(f"Database initialization failed. Check your credentials/server. Error: {str(e)}") from e

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for managing SQLAlchemy session lifecycle and transactional rollback."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except (OperationalError, SQLAlchemyError) as e:
        session.rollback()
        logger.error(f"Database exception encountered. Transaction rolled back: {str(e)}")
        raise DatabaseError(f"Database connection or statement error: {str(e)}") from e
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error encountered. Transaction rolled back: {str(e)}")
        raise DatabaseError(f"Unexpected persistence error: {str(e)}") from e
    finally:
        session.close()

"""
Database connection and session management
Supports both SQLite (local) and PostgreSQL (production)
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from backend.config import settings
from backend.base import Base  # noqa: F401

# Import all models to register them with Base
from backend.models import Product, Note, Comment, AnalysisResult, Task  # noqa: F401


def get_engine():
    """Create database engine based on DATABASE_URL"""
    db_url = settings.database_url

    if db_url.startswith("sqlite"):
        # SQLite configuration
        engine = create_engine(
            db_url,
            echo=settings.debug,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            future=True
        )
    else:
        # PostgreSQL/MySQL configuration
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
        from sqlalchemy.pool import NullPool

        # Convert sync URL to async URL
        async_db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
        async_db_url = async_db_url.replace("mysql://", "mysql+aiomysql://")

        engine = create_async_engine(
            async_db_url,
            echo=settings.debug,
            poolclass=NullPool,
            future=True
        )

    return engine


# Create engine
engine = get_engine()


def get_session_factory():
    """Get session factory based on database type"""
    db_url = settings.database_url

    if db_url.startswith("sqlite"):
        # SQLite uses sync session
        return sessionmaker(autocommit=False, autoflush=False, bind=engine)
    else:
        # PostgreSQL uses async session
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
        return async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )


# Create session factory
async_session_factory = get_session_factory()


# Base class for models (imported from base.py for circular import resolution)
Base = Base


def get_db():
    """
    Dependency for getting database session (sync for SQLite)
    """
    db_url = settings.database_url

    if db_url.startswith("sqlite"):
        # Sync session for SQLite
        db = async_session_factory()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    else:
        # Async session for PostgreSQL
        from sqlalchemy.ext.asyncio import AsyncSession

        async def async_get_db():
            async with async_session_factory() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise
                finally:
                    await session.close()

        return async_get_db()


async def init_db():
    """
    Initialize database tables
    """
    db_url = settings.database_url

    if db_url.startswith("sqlite"):
        # SQLite: sync approach
        Base.metadata.create_all(bind=engine)
    else:
        # PostgreSQL: async approach
        from sqlalchemy.ext.asyncio import create_async_engine

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Close database connections
    """
    db_url = settings.database_url

    if not db_url.startswith("sqlite"):
        await engine.dispose()

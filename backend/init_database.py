"""
Database initialization script
Run this to create all tables
"""
import asyncio
from backend.database import init_db, engine, Base
from backend.models import Product, Note, Comment, AnalysisResult, Task


async def main():
    """Initialize database tables"""
    print("Creating database tables...")
    print(f"Models to create: {list(Base.metadata.tables.keys())}")

    await init_db()

    print("Database tables created successfully!")
    print(f"Tables: {list(Base.metadata.tables.keys())}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

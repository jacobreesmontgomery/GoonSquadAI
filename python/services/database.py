from os import getenv
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, scoped_session

load_dotenv()

# Database configuration for synchronous operations
db_url = (
    f"postgresql://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}"
    f"@{getenv('DB_HOST')}:{getenv('DB_PORT')}/{getenv('DB_NAME')}"
)

# Database configuration for asynchronous operations
async_db_url = (
    f"postgresql+asyncpg://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}"
    f"@{getenv('DB_HOST')}:{getenv('DB_PORT')}/{getenv('DB_NAME')}"
)


class DatabaseService:
    """
    Database service for interacting with the PostgreSQL database.
    Supports both synchronous and asynchronous operations.
    """

    def __init__(self):
        # Create the synchronous SQLAlchemy engine with connection pooling
        self.engine = create_engine(
            db_url,
            pool_size=10,  # Maximum connections in the pool
            max_overflow=5,  # Additional connections allowed above pool_size
            pool_timeout=30,  # Wait timeout for connections
            pool_pre_ping=True,  # Ensures connections are alive
        )

        # Create the asynchronous SQLAlchemy engine
        self.async_engine = create_async_engine(
            async_db_url,
            pool_size=10,
            max_overflow=5,
            pool_timeout=30,
            pool_pre_ping=True,
        )

        # Synchronous scoped session factory
        self.Session = scoped_session(sessionmaker(bind=self.engine))

        # Asynchronous session factory
        self.AsyncSessionFactory = sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    def get_session(self):
        """
        Get a new synchronous database session.
        """
        return self.Session()

    def close_session(self):
        """
        Remove the current synchronous session from the scoped session registry.
        """
        self.Session.remove()

    def get_async_session(self):
        """
        Get a new asynchronous database session.
        This returns an async context manager for use with 'async with'.
        """

        @asynccontextmanager
        async def _get_async_session():
            session = self.AsyncSessionFactory()
            try:
                yield session
            finally:
                await session.close()

        return _get_async_session()

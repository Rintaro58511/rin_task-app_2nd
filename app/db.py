from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

ASYNC_DB_URL = "postgresql+asyncpg://postgres:password123@db:5432/task_db"

async_engine = create_async_engine(ASYNC_DB_URL, echo=True)

async_session_factory = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)

Base = declarative_base()


async def get_db_session():
    async with async_session_factory() as session:
        yield session

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os
from sqlalchemy import URL

DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")

ASYNC_DB_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=DATABASE_USER,
    password=DATABASE_PASSWORD,
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    database=DATABASE_NAME,
)

async_engine = create_async_engine(ASYNC_DB_URL, echo=True)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db_session():
    async with async_session() as session:
        yield session

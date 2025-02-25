from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config import Config
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import AsyncGenerator

async_engine = create_async_engine(url=Config.DATABASE_URL)
Session = async_sessionmaker(bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def initdb() -> None:
    async with async_engine.begin() as conn:
        from src.database.models import Book
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with Session() as session:
        yield session

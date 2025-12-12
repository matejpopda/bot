from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, DeclarativeMeta
from sqlalchemy.ext.asyncio import async_sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///sqlite-database.db"
engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


Base: DeclarativeMeta = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

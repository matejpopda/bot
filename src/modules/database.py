from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, DeclarativeMeta


DATABASE_URL = "sqlite+aiosqlite:///sqllite-database.db"
engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


Base: DeclarativeMeta = declarative_base()

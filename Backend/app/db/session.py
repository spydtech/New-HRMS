# from collections.abc import AsyncGenerator

# from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# from app.core.config import settings

# engine = create_async_engine(
#     settings.database_url,
#     echo=settings.DEBUG,
#     pool_pre_ping=True,
#     pool_size=10,
#     max_overflow=20,
#     pool_recycle=3600,   # MySQL closes idle conns after wait_timeout (default 8h); recycle sooner
# )

# SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# async def get_db() -> AsyncGenerator[AsyncSession, None]:
#     async with SessionLocal() as session:
#         try:
#             yield session
#         except Exception:
#             await session.rollback()
#             raise




from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)


@event.listens_for(engine.sync_engine, "connect")
def _set_mysql_collation(dbapi_connection, connection_record):
    """
    aiomysql's connect() does not accept a `collation` kwarg, so we set it
    on every new connection via SET NAMES.
    """
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute(
            f"SET NAMES {settings.MYSQL_CHARSET} COLLATE {settings.MYSQL_COLLATION}"
        )
    finally:
        cursor.close()


SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
# app/main.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import (
    Boolean, Date, DateTime, Float, Integer, String, Text, text,
)
from sqlalchemy.dialects.mysql import BIGINT

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.seed import seed_leave_types, seed_super_admin
from app.db.base import Base
from app.db.session import engine
from app.exceptions import register_exception_handlers
import app.models  # noqa: F401 — registers all models

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _column_ddl(col) -> str:
    t = col.type
    nullable = "" if col.nullable else " NOT NULL"

    if isinstance(t, Boolean):
        return f"TINYINT(1){nullable}"
    if isinstance(t, Float):
        return f"FLOAT{nullable}"
    if isinstance(t, BIGINT):
        return f"BIGINT UNSIGNED{nullable}"
    if isinstance(t, Integer):
        return f"INT{nullable}"
    if isinstance(t, String):
        return f"VARCHAR({t.length or 255}){nullable}"
    if isinstance(t, Text):
        return f"TEXT{nullable}"
    if isinstance(t, Date):
        return f"DATE{nullable}"
    if isinstance(t, DateTime):
        return f"DATETIME{nullable}"
    return f"VARCHAR(255){nullable}"


async def _ensure_columns() -> None:
    async with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            res = await conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = DATABASE() AND table_name = :t"
                ),
                {"t": table.name},
            )
            existing = {row[0] for row in res}

            for col in table.columns:
                if col.name in existing:
                    continue
                ddl = _column_ddl(col)
                logger.warning(
                    "Adding missing column %s.%s [%s]",
                    table.name, col.name, ddl,
                )
                await conn.execute(
                    text(f"ALTER TABLE `{table.name}` ADD COLUMN `{col.name}` {ddl}")
                )
                logger.info("Added %s.%s", table.name, col.name)


async def _ensure_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _ensure_columns()
    logger.info("Ensured all tables and columns exist.")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting %s (%s)", settings.APP_NAME, settings.ENVIRONMENT)
    try:
        await _ensure_tables()
        await seed_super_admin()
        await seed_leave_types()
    except Exception as exc:
        logger.exception("Startup task failed: %s", exc)
    yield
    await engine.dispose()
    logger.info("Shutdown complete")


def _add_cors(app: FastAPI) -> None:
    if settings.is_production:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
    )
    _add_cors(app)
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    return app


app = create_app()


# # app/main.py
# import logging
# from contextlib import asynccontextmanager

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy import text

# from app.api.v1.router import api_router
# from app.core.config import settings
# from app.core.seed import seed_leave_types, seed_super_admin
# from app.db.base import Base
# from app.db.session import engine
# from app.exceptions import register_exception_handlers
# import app.models  # noqa: F401 — registers all models

# logging.basicConfig(
#     level=logging.DEBUG if settings.DEBUG else logging.INFO,
#     format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
# )
# logger = logging.getLogger(__name__)


# # Idempotent column additions for local dev.
# # Each tuple: (table, column, ddl_after_col_name)
# _DEV_COLUMNS_TO_ENSURE = [
#     ("projects", "progress", "INT NOT NULL DEFAULT 0"),
# ]


# async def _ensure_columns() -> None:
#     async with engine.begin() as conn:
#         for table, col, ddl in _DEV_COLUMNS_TO_ENSURE:
#             result = await conn.execute(
#                 text(
#                     "SELECT COUNT(*) FROM information_schema.columns "
#                     "WHERE table_schema = DATABASE() "
#                     "AND table_name = :t AND column_name = :c"
#                 ),
#                 {"t": table, "c": col},
#             )
#             if result.scalar() == 0:
#                 logger.warning("Adding missing column %s.%s", table, col)
#                 await conn.execute(
#                     text(f"ALTER TABLE {table} ADD COLUMN {col} {ddl}")
#                 )
#                 logger.info("Added %s.%s", table, col)


# async def _ensure_tables() -> None:
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     await _ensure_columns()
#     logger.info("Ensured all tables and columns exist.")


# @asynccontextmanager
# async def lifespan(_: FastAPI):
#     logger.info("Starting %s (%s)", settings.APP_NAME, settings.ENVIRONMENT)
#     try:
#         await _ensure_tables()
#         await seed_super_admin()
#         await seed_leave_types()
#     except Exception as exc:
#         logger.exception("Startup task failed: %s", exc)
#     yield
#     await engine.dispose()
#     logger.info("Shutdown complete")


# def _add_cors(app: FastAPI) -> None:
#     if settings.is_production:
#         app.add_middleware(
#             CORSMiddleware,
#             allow_origins=settings.CORS_ORIGINS,
#             allow_credentials=True,
#             allow_methods=["*"],
#             allow_headers=["*"],
#         )
#     else:
#         app.add_middleware(
#             CORSMiddleware,
#             allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
#             allow_credentials=True,
#             allow_methods=["*"],
#             allow_headers=["*"],
#         )


# def create_app() -> FastAPI:
#     app = FastAPI(
#         title=settings.APP_NAME,
#         version="1.0.0",
#         lifespan=lifespan,
#         docs_url="/docs" if not settings.is_production else None,
#         redoc_url="/redoc" if not settings.is_production else None,
#     )
#     _add_cors(app)
#     register_exception_handlers(app)
#     app.include_router(api_router, prefix=settings.API_V1_PREFIX)
#     return app


# app = create_app()
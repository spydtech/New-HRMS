# from functools import lru_cache

# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):
#     model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=True)

#     APP_NAME: str = "HRMS Backend"
#     ENVIRONMENT: str = "development"
#     DEBUG: bool = True
#     API_V1_PREFIX: str = "/api/v1"

#     SECRET_KEY: str = "change-me-in-production"
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

#     MYSQL_HOST: str = "localhost"
#     MYSQL_PORT: int = 3306
#     MYSQL_USER: str = "root"
#     MYSQL_PASSWORD: str = "root"
#     MYSQL_DB: str = "app"

#     CORS_ORIGINS: list[str] = [
#         "http://localhost:3000",
#         "http://localhost:5173",
#         "http://localhost:5174",
#         "http://127.0.0.1:3000",
#         "http://127.0.0.1:5173",
#         "http://127.0.0.1:5174"
#     ]

#     # Auto-seeded on startup
#     SUPER_ADMIN_NAME: str = "Super Admin"
#     SUPER_ADMIN_EMAIL: str = "superadmin@hrms.com"
#     SUPER_ADMIN_PASSWORD: str = "SuperAdmin@123"

#     @property
#     def database_url(self) -> str:
#         return (
#             f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
#             f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"
#         )

#     @property
#     def is_production(self) -> bool:
#         return self.ENVIRONMENT == "production"


# @lru_cache
# def get_settings() -> Settings:
#     return Settings()


# settings = get_settings()


from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=True)

    APP_NAME: str = "HRMS Backend"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DB: str = "app"

    MYSQL_SCHEMA: str = "app"
    MYSQL_CHARSET: str = "utf8mb4"
    MYSQL_COLLATION: str = "utf8mb4_unicode_ci"

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]

    SUPER_ADMIN_NAME: str = "Super Admin"
    SUPER_ADMIN_EMAIL: str = "superadmin@hrms.com"
    SUPER_ADMIN_PASSWORD: str = "SuperAdmin@123"

    @property
    def database_url(self) -> str:
        # NOTE: aiomysql does NOT accept `collation` as a connect() kwarg.
        # Collation is applied per-connection via a "connect" event listener
        # (see app/db/session.py). Only pass `charset` here.
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
            f"?charset={self.MYSQL_CHARSET}"
        )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
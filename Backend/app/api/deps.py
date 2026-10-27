from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.exceptions import ForbiddenError, UnauthorizedError
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

bearer_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_user_service(session: DbSession) -> UserService:
    return UserService(UserRepository(session))


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def _user_from_credentials(
    service: UserService, credentials: HTTPAuthorizationCredentials | None
) -> User | None:
    if credentials is None:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
    return await service.repo.get(user_id)


async def get_current_user(
    service: UserServiceDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    user = await _user_from_credentials(service, credentials)
    if user is None:
        raise UnauthorizedError("Not authenticated")
    if not user.is_active:
        raise UnauthorizedError("Account is disabled")
    return user


async def get_optional_current_user(
    service: UserServiceDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User | None:
    return await _user_from_credentials(service, credentials)


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_current_user)]


def require_roles(*roles: UserRole):
    async def _checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise ForbiddenError("Insufficient permissions")
        return user

    return _checker


def require_super_admin(user: CurrentUser) -> User:
    if user.role != UserRole.super_admin:
        raise ForbiddenError("Super admin access required")
    return user


CurrentSuperAdmin = Annotated[User, Depends(require_super_admin)]
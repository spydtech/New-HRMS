from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession, UserServiceDep
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
async def list_users(
    _: CurrentUser,
    service: UserServiceDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    return await service.list_users(offset=offset, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, _: CurrentUser, service: UserServiceDep):
    return await service.get_or_404(user_id)
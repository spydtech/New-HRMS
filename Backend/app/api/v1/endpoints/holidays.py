from datetime import date as DateType

from fastapi import APIRouter, status
from sqlalchemy import extract, select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.holiday import Holiday
from app.models.user import UserRole
from app.schemas.holiday import (
    HolidayCreate,
    HolidayRead,
    HolidayUpdate,
    holiday_to_response,
)

router = APIRouter(prefix="/holidays", tags=["holidays"])

HR_ROLES = (UserRole.super_admin, UserRole.hr_admin, UserRole.admin)


def _is_hr(user) -> bool:
    return user.role in HR_ROLES


def _day_name(d: DateType) -> str:
    return d.strftime("%A")


@router.get("", response_model=list[HolidayRead])
async def list_holidays(
    session: DbSession,
    _: CurrentUser,
    year: int | None = None,
):
    stmt = select(Holiday).where(Holiday.is_active.is_(True))
    if year is not None:
        stmt = stmt.where(extract("year", Holiday.date) == year)
    stmt = stmt.order_by(Holiday.date.asc())
    result = await session.execute(stmt)
    return [holiday_to_response(h) for h in result.scalars().all()]


@router.get("/{holiday_id}", response_model=HolidayRead)
async def get_holiday(holiday_id: int, session: DbSession, _: CurrentUser):
    record = await session.get(Holiday, holiday_id)
    if not record:
        raise NotFoundError("Holiday not found")
    return holiday_to_response(record)


@router.post("", response_model=HolidayRead, status_code=status.HTTP_201_CREATED)
async def create_holiday(
    payload: HolidayCreate,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can add holidays")

    existing = await session.execute(
        select(Holiday).where(
            Holiday.date == payload.date,
            Holiday.holiday_name == payload.holiday_name,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError("A holiday with this date and name already exists")

    record = Holiday(
        day=payload.day or _day_name(payload.date),
        date=payload.date,
        holiday_name=payload.holiday_name,
        description=payload.description,
        holiday_type=payload.holiday_type or "Public",
        is_active=True,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return holiday_to_response(record)


@router.put("/{holiday_id}", response_model=HolidayRead)
async def update_holiday(
    holiday_id: int,
    payload: HolidayUpdate,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can update holidays")

    record = await session.get(Holiday, holiday_id)
    if not record:
        raise NotFoundError("Holiday not found")

    data = payload.model_dump(exclude_unset=True, by_alias=False)
    for field, value in data.items():
        if value is not None:
            setattr(record, field, value)

    if "date" in data and "day" not in data:
        record.day = _day_name(record.date)

    await session.commit()
    await session.refresh(record)
    return holiday_to_response(record)


@router.delete("/{holiday_id}")
async def delete_holiday(
    holiday_id: int,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can delete holidays")

    record = await session.get(Holiday, holiday_id)
    if not record:
        raise NotFoundError("Holiday not found")

    await session.delete(record)
    await session.commit()
    return {"success": True, "message": "Holiday deleted"}


@router.delete("/by-name/{name}")
async def delete_holiday_by_name(
    name: str,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can delete holidays")

    result = await session.execute(
        select(Holiday).where(Holiday.holiday_name == name)
    )
    rows = list(result.scalars().all())
    if not rows:
        raise NotFoundError("Holiday not found")

    for row in rows:
        await session.delete(row)
    await session.commit()
    return {"success": True, "message": "Holiday deleted"}
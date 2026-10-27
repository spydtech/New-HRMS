from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import ForbiddenError, NotFoundError
from app.models.event import Event
from app.models.user import User, UserRole
from app.schemas.event import EventCreate, EventRead, EventUpdate

router = APIRouter(prefix="/events", tags=["events"])

HR_ROLES = (UserRole.super_admin, UserRole.hr_admin, UserRole.admin)


def _is_hr(user) -> bool:
    return user.role in HR_ROLES


async def _resolve_employees(session, ids: list[int]) -> list[User]:
    if not ids:
        return []
    result = await session.execute(select(User).where(User.id.in_(ids)))
    return list(result.scalars().all())


@router.get("", response_model=list[EventRead])
async def list_events(session: DbSession, _: CurrentUser):
    result = await session.execute(select(Event).order_by(Event.event_date.desc()))
    return list(result.scalars().all())


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreate,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can create events")

    employees = await _resolve_employees(session, payload.employee_ids)

    event = Event(
        name=payload.name,
        event_date=payload.event_date,
        description=payload.description,
    )
    event.assigned_employees = employees

    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


@router.put("/{event_id}", response_model=EventRead)
async def update_event(
    event_id: int,
    payload: EventUpdate,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can update events")

    event = await session.get(Event, event_id)
    if not event:
        raise NotFoundError("Event not found")

    data = payload.model_dump(exclude_unset=True, by_alias=False)
    
    if "name" in data:
        event.name = data["name"]
    if "event_date" in data:
        event.event_date = data["event_date"]
    if "description" in data:
        event.description = data["description"]
    
    # Update employee assignments if provided
    if "employee_ids" in data and data["employee_ids"] is not None:
        event.assigned_employees = await _resolve_employees(
            session, data["employee_ids"]
        )

    await session.commit()
    await session.refresh(event)
    return event


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can delete events")

    event = await session.get(Event, event_id)
    if not event:
        raise NotFoundError("Event not found")

    await session.delete(event)
    await session.commit()
    return {"success": True, "message": "Event deleted"}
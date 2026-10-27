from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.team import Team
from app.models.user import User, UserRole
from app.schemas.team import TeamCreate, TeamRead, TeamUpdate, team_to_response

router = APIRouter(prefix="/teams", tags=["teams"])

HR_ROLES = (UserRole.super_admin, UserRole.hr_admin, UserRole.admin)


def _is_hr(user) -> bool:
    return user.role in HR_ROLES


async def _resolve_members(session, ids: list[int]) -> list[User]:
    if not ids:
        return []
    result = await session.execute(select(User).where(User.id.in_(ids)))
    return list(result.scalars().all())


@router.get("", response_model=list[TeamRead])
async def list_teams(session: DbSession, _: CurrentUser):
    result = await session.execute(select(Team).order_by(Team.team_name))
    return [team_to_response(t) for t in result.scalars().all()]


@router.get("/{team_id}", response_model=TeamRead)
async def get_team(team_id: int, session: DbSession, _: CurrentUser):
    team = await session.get(Team, team_id)
    if not team:
        raise NotFoundError("Team not found")
    return team_to_response(team)


@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(
    payload: TeamCreate,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can create teams")

    existing = await session.execute(
        select(Team).where(Team.team_name == payload.team_name)
    )
    if existing.scalar_one_or_none():
        raise ConflictError("A team with this name already exists")

    members = await _resolve_members(session, payload.member_ids)

    team = Team(
        team_name=payload.team_name,
        description=payload.description,
        image=payload.image,
        lead_id=payload.lead_id,
    )
    team.members = members

    session.add(team)
    await session.commit()
    await session.refresh(team)
    return team_to_response(team)


@router.put("/{team_id}", response_model=TeamRead)
async def update_team(
    team_id: int,
    payload: TeamUpdate,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can update teams")

    team = await session.get(Team, team_id)
    if not team:
        raise NotFoundError("Team not found")

    data = payload.model_dump(exclude_unset=True, by_alias=False)
    if "team_name" in data and data["team_name"]:
        team.team_name = data["team_name"]
    if "description" in data:
        team.description = data["description"]
    if "image" in data:
        team.image = data["image"]
    if "lead_id" in data:
        team.lead_id = data["lead_id"]
    if "member_ids" in data and data["member_ids"] is not None:
        team.members = await _resolve_members(session, data["member_ids"])

    await session.commit()
    await session.refresh(team)
    return team_to_response(team)


@router.delete("/{team_id}")
async def delete_team(
    team_id: int,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can delete teams")

    team = await session.get(Team, team_id)
    if not team:
        raise NotFoundError("Team not found")

    await session.delete(team)
    await session.commit()
    return {"success": True, "message": "Team deleted"}
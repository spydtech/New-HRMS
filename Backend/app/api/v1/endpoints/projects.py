# from fastapi import APIRouter, status
# from sqlalchemy import select

# from app.api.deps import CurrentUser, DbSession
# from app.exceptions import ConflictError, ForbiddenError, NotFoundError
# from app.models.client import Client
# from app.models.project import Project
# from app.models.team import Team
# from app.models.user import User, UserRole
# from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

# router = APIRouter(prefix="/projects", tags=["projects"])

# HR_ROLES = (UserRole.super_admin, UserRole.hr_admin, UserRole.admin)


# def _is_hr(user) -> bool:
#     return user.role in HR_ROLES


# async def _validate_relations(session, client_id, team_id, team_lead_id):
#     if client_id is not None:
#         if not await session.get(Client, client_id):
#             raise NotFoundError(f"Client {client_id} not found")
#     if team_id is not None:
#         if not await session.get(Team, team_id):
#             raise NotFoundError(f"Team {team_id} not found")
#     if team_lead_id is not None:
#         if not await session.get(User, team_lead_id):
#             raise NotFoundError(f"Team lead {team_lead_id} not found")


# @router.get("", response_model=list[ProjectRead])
# async def list_projects(session: DbSession, _: CurrentUser):
#     result = await session.execute(select(Project).order_by(Project.project_name))
#     return list(result.scalars().all())


# @router.get("/{project_id}", response_model=ProjectRead)
# async def get_project(project_id: int, session: DbSession, _: CurrentUser):
#     project = await session.get(Project, project_id)
#     if not project:
#         raise NotFoundError("Project not found")
#     return project


# @router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
# async def create_project(
#     payload: ProjectCreate,
#     session: DbSession,
#     current_user: CurrentUser,
# ):
#     if not _is_hr(current_user):
#         raise ForbiddenError("Only HR can create projects")

#     await _validate_relations(
#         session, payload.client_id, payload.team_id, payload.team_lead_id
#     )

#     existing = await session.execute(
#         select(Project).where(Project.project_name == payload.project_name)
#     )
#     if existing.scalar_one_or_none():
#         raise ConflictError("A project with this name already exists")

#     project = Project(
#         project_name=payload.project_name.strip(),
#         description=payload.description,
#         client_id=payload.client_id,
#         team_id=payload.team_id,
#         team_lead_id=payload.team_lead_id,
#         start_date=payload.start_date,
#         end_date=payload.end_date,
#         project_priority=payload.project_priority,
#         rate=payload.rate,
#         rate_type=payload.rate_type,
#         status=payload.status or "Active",
#         project_image=payload.project_image,
#     )
#     session.add(project)
#     await session.commit()
#     await session.refresh(project)
#     return project


# @router.put("/{project_id}", response_model=ProjectRead)
# async def update_project(
#     project_id: int,
#     payload: ProjectUpdate,
#     session: DbSession,
#     current_user: CurrentUser,
# ):
#     if not _is_hr(current_user):
#         raise ForbiddenError("Only HR can update projects")

#     project = await session.get(Project, project_id)
#     if not project:
#         raise NotFoundError("Project not found")

#     data = payload.model_dump(exclude_unset=True, by_alias=False)

#     await _validate_relations(
#         session,
#         data.get("client_id"),
#         data.get("team_id"),
#         data.get("team_lead_id"),
#     )

#     for field in (
#         "project_name", "description", "client_id", "team_id", "team_lead_id",
#         "start_date", "end_date", "project_priority", "rate", "rate_type",
#         "status", "project_image",
#     ):
#         if field in data:
#             setattr(project, field, data[field])

#     await session.commit()
#     await session.refresh(project)
#     return project


# @router.delete("/{project_id}")
# async def delete_project(
#     project_id: int,
#     session: DbSession,
#     current_user: CurrentUser,
# ):
#     if not _is_hr(current_user):
#         raise ForbiddenError("Only HR can delete projects")

#     project = await session.get(Project, project_id)
#     if not project:
#         raise NotFoundError("Project not found")

#     await session.delete(project)
#     await session.commit()
#     return {"success": True, "message": "Project deleted"}


import json

from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.client import Client
from app.models.project import Project
from app.models.project_activity import ProjectActivity
from app.models.team import Team
from app.models.user import User, UserRole
from app.schemas.project import (
    ProjectCreate,
    ProjectProgressUpdate,
    ProjectRead,
    ProjectUpdate,
)
from app.schemas.project_activity import (
    ProjectActivityCreate,
    ProjectActivityRead,
)

router = APIRouter(prefix="/projects", tags=["projects"])

HR_ROLES = (UserRole.super_admin, UserRole.hr_admin, UserRole.admin)


def _is_hr(user) -> bool:
    return user.role in HR_ROLES


async def _validate_relations(session, client_id, team_id, team_lead_id):
    if client_id is not None:
        if not await session.get(Client, client_id):
            raise NotFoundError(f"Client {client_id} not found")
    if team_id is not None:
        if not await session.get(Team, team_id):
            raise NotFoundError(f"Team {team_id} not found")
    if team_lead_id is not None:
        if not await session.get(User, team_lead_id):
            raise NotFoundError(f"Team lead {team_lead_id} not found")


def _serialize_activity(activity: ProjectActivity) -> dict:
    attachments = []
    if activity.attachments_json:
        try:
            attachments = json.loads(activity.attachments_json) or []
        except (ValueError, TypeError):
            attachments = []

    user_payload = None
    if activity.user:
        user_payload = {
            "id": activity.user.id,
            "name": activity.user.name,
            "email": activity.user.email,
            "profileImage": activity.user.profile_image,
            "designation": activity.user.designation,
        }

    return {
        "id": activity.id,
        "projectId": activity.project_id,
        "content": activity.content,
        "activityType": activity.activity_type,
        "attachments": attachments,
        "user": user_payload,
        "createdAt": activity.created_at,
    }


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------
@router.get("", response_model=list[ProjectRead])
async def list_projects(session: DbSession, _: CurrentUser):
    result = await session.execute(select(Project).order_by(Project.project_name))
    return list(result.scalars().all())


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: int, session: DbSession, _: CurrentUser):
    project = await session.get(Project, project_id)
    if not project:
        raise NotFoundError("Project not found")
    return project


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can create projects")

    await _validate_relations(
        session, payload.client_id, payload.team_id, payload.team_lead_id
    )

    existing = await session.execute(
        select(Project).where(Project.project_name == payload.project_name)
    )
    if existing.scalar_one_or_none():
        raise ConflictError("A project with this name already exists")

    project = Project(
        project_name=payload.project_name.strip(),
        description=payload.description,
        client_id=payload.client_id,
        team_id=payload.team_id,
        team_lead_id=payload.team_lead_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        project_priority=payload.project_priority,
        rate=payload.rate,
        rate_type=payload.rate_type,
        status=payload.status or "Active",
        progress=max(0, min(100, int(payload.progress or 0))),
        project_image=payload.project_image,
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    payload: ProjectUpdate,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can update projects")

    project = await session.get(Project, project_id)
    if not project:
        raise NotFoundError("Project not found")

    data = payload.model_dump(exclude_unset=True, by_alias=False)

    await _validate_relations(
        session,
        data.get("client_id"),
        data.get("team_id"),
        data.get("team_lead_id"),
    )

    for field in (
        "project_name",
        "description",
        "client_id",
        "team_id",
        "team_lead_id",
        "start_date",
        "end_date",
        "project_priority",
        "rate",
        "rate_type",
        "status",
        "progress",
        "project_image",
    ):
        if field in data:
            value = data[field]
            if field == "progress" and value is not None:
                value = max(0, min(100, int(value)))
            setattr(project, field, value)

    await session.commit()
    await session.refresh(project)
    return project


@router.patch("/{project_id}/progress", response_model=ProjectRead)
async def update_project_progress(
    project_id: int,
    payload: ProjectProgressUpdate,
    session: DbSession,
    current_user: CurrentUser,
):
    """Update only the progress field. Any authenticated user can do this."""
    project = await session.get(Project, project_id)
    if not project:
        raise NotFoundError("Project not found")

    project.progress = max(0, min(100, int(payload.progress)))
    await session.commit()
    await session.refresh(project)
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can delete projects")

    project = await session.get(Project, project_id)
    if not project:
        raise NotFoundError("Project not found")

    await session.delete(project)
    await session.commit()
    return {"success": True, "message": "Project deleted"}


# ---------------------------------------------------------------------------
# Activities
# ---------------------------------------------------------------------------
@router.get(
    "/{project_id}/activities", response_model=list[ProjectActivityRead]
)
async def list_project_activities(
    project_id: int,
    session: DbSession,
    _: CurrentUser,
):
    project = await session.get(Project, project_id)
    if not project:
        raise NotFoundError("Project not found")

    result = await session.execute(
        select(ProjectActivity)
        .where(ProjectActivity.project_id == project_id)
        .order_by(ProjectActivity.created_at.desc())
    )
    return [_serialize_activity(a) for a in result.scalars().all()]


@router.post(
    "/{project_id}/activities",
    response_model=ProjectActivityRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_project_activity(
    project_id: int,
    payload: ProjectActivityCreate,
    session: DbSession,
    current_user: CurrentUser,
):
    project = await session.get(Project, project_id)
    if not project:
        raise NotFoundError("Project not found")

    content = (payload.content or "").strip()
    if not content:
        raise ConflictError("Activity content is required")

    activity = ProjectActivity(
        project_id=project_id,
        user_id=current_user.id,
        content=content,
        activity_type=payload.activityType or "message",
        attachments_json=(
            json.dumps(payload.attachments) if payload.attachments else None
        ),
    )
    session.add(activity)

    # Optionally update progress in the same call
    if getattr(payload, "progress", None) is not None:
        project.progress = max(0, min(100, int(payload.progress)))

    await session.commit()
    await session.refresh(activity)
    return _serialize_activity(activity)


@router.get("/{project_id}/members")
async def list_project_members(
    project_id: int,
    session: DbSession,
    _: CurrentUser,
):
    project = await session.get(Project, project_id)
    if not project:
        raise NotFoundError("Project not found")

    members = []
    if project.team and project.team.members:
        for u in project.team.members:
            members.append(
                {
                    "id": u.id,
                    "name": u.name,
                    "email": u.email,
                    "role": u.role,
                    "designation": u.designation,
                    "profileImage": u.profile_image,
                }
            )

    lead = project.team_lead
    lead_payload = (
        {
            "id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "designation": lead.designation,
            "profileImage": lead.profile_image,
        }
        if lead
        else None
    )

    return {"members": members, "lead": lead_payload}
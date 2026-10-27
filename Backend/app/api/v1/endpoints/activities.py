import json

from fastapi import APIRouter
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.models.project import Project
from app.models.project_activity import ProjectActivity
from app.models.team import Team, team_members
from app.models.user import UserRole

router = APIRouter(prefix="/activities", tags=["activities"])

HR_ROLES = (UserRole.super_admin, UserRole.hr_admin, UserRole.admin)


def _serialize_user(u) -> dict | None:
    if not u:
        return None
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "profileImage": u.profile_image,
        "designation": u.designation,
    }


def _serialize_activity(
    activity: ProjectActivity,
    project: Project | None,
    team_members_list: list | None = None,
) -> dict:
    attachments = []
    if activity.attachments_json:
        try:
            attachments = json.loads(activity.attachments_json) or []
        except (ValueError, TypeError):
            attachments = []

    project_payload = None
    if project:
        project_payload = {
            "id": project.id,
            "name": project.project_name,
            "status": project.status,
            "progress": project.progress,
            "teamId": project.team_id,
            "teamName": project.team.team_name if project.team else None,
            "teamMembers": [
                _serialize_user(m) for m in (team_members_list or [])
            ],
        }

    return {
        "id": activity.id,
        "projectId": activity.project_id,
        "content": activity.content,
        "activityType": activity.activity_type,
        "attachments": attachments,
        "user": _serialize_user(activity.user),
        "project": project_payload,
        "createdAt": activity.created_at,
    }


@router.get("")
async def list_all_activities(
    session: DbSession, _: CurrentUser, limit: int = 50
):
    """Return the most recent activities across all projects."""
    result = await session.execute(
        select(ProjectActivity)
        .options(selectinload(ProjectActivity.user))
        .order_by(ProjectActivity.created_at.desc())
        .limit(max(1, min(limit, 200)))
    )
    activities = list(result.scalars().all())

    project_ids = {a.project_id for a in activities if a.project_id}

    projects_by_id: dict[int, Project] = {}
    members_by_team_id: dict[int, list] = {}

    if project_ids:
        proj_result = await session.execute(
            select(Project)
            .where(Project.id.in_(project_ids))
            .options(selectinload(Project.team))
        )
        for p in proj_result.scalars().all():
            projects_by_id[p.id] = p

        team_ids = {p.team_id for p in projects_by_id.values() if p.team_id}
        if team_ids:
            team_result = await session.execute(
                select(Team)
                .where(Team.id.in_(team_ids))
                .options(selectinload(Team.members))
            )
            for t in team_result.scalars().all():
                members_by_team_id[t.id] = list(t.members or [])

    out = []
    for a in activities:
        proj = projects_by_id.get(a.project_id)
        team_members_list = (
            members_by_team_id.get(proj.team_id, []) if proj else []
        )
        out.append(_serialize_activity(a, proj, team_members_list))

    return out


@router.get("/my-projects")
async def list_my_projects(session: DbSession, current_user: CurrentUser):
    """
    Projects the current user can post updates to.

    - HR / Admin / Super Admin: every project.
    - Regular user: only projects where they are the team lead
      OR belong to the assigned team.
    """
    # HR & admins see everything
    if current_user.role in HR_ROLES:
        result = await session.execute(
            select(Project).order_by(Project.project_name)
        )
        return [
            {
                "id": p.id,
                "name": p.project_name,
                "status": p.status,
                "progress": p.progress,
            }
            for p in result.scalars().all()
        ]

    # 1) Find team IDs the user is a member of
    team_result = await session.execute(
        select(team_members.c.team_id).where(
            team_members.c.user_id == current_user.id
        )
    )
    my_team_ids = [
        row[0] for row in team_result.all() if row[0] is not None
    ]

    # 2) Find projects where they're lead OR in one of those teams
    conditions = [Project.team_lead_id == current_user.id]
    if my_team_ids:
        conditions.append(Project.team_id.in_(my_team_ids))

    result = await session.execute(
        select(Project)
        .where(or_(*conditions))
        .order_by(Project.project_name)
    )

    return [
        {
            "id": p.id,
            "name": p.project_name,
            "status": p.status,
            "progress": p.progress,
        }
        for p in result.scalars().all()
    ]
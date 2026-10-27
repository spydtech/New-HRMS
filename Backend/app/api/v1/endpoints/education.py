from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import ForbiddenError, NotFoundError
from app.models.education import Education
from app.models.user import UserRole
from app.schemas.education import EducationRead, EducationUpsert

router = APIRouter(prefix="/education", tags=["education"])

HR_ROLES = (UserRole.super_admin, UserRole.hr_admin, UserRole.admin)


@router.get("/fetchEducation", response_model=list[EducationRead])
async def fetch_education(session: DbSession, current_user: CurrentUser):
    result = await session.execute(
        select(Education).where(Education.user_id == current_user.id).order_by(Education.id)
    )
    return list(result.scalars().all())


@router.post("/saveOrUpdate", response_model=EducationRead, status_code=status.HTTP_201_CREATED)
async def save_or_update_education(
    payload: EducationUpsert,
    session: DbSession,
    current_user: CurrentUser,
):
    # Upsert by single education record per user (matches legacy single-object API)
    existing = await session.execute(
        select(Education).where(Education.user_id == current_user.id).order_by(Education.id)
    )
    rows = list(existing.scalars().all())

    if rows:
        record = rows[0]
        record.degree = payload.degree or record.degree
        record.institution = payload.institution or record.institution
        record.university = payload.university or record.university
        record.start_year = payload.startYear or record.start_year
        record.end_year = payload.endYear or record.end_year
        await session.commit()
        await session.refresh(record)
        return record

    record = Education(
        user_id=current_user.id,
        employee_id=current_user.employee_id,
        degree=payload.degree,
        institution=payload.institution,
        university=payload.university,
        start_year=payload.startYear,
        end_year=payload.endYear,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


@router.delete("/delete")
async def delete_education(
    session: DbSession,
    current_user: CurrentUser,
    education_id: int | None = None,
):
    stmt = select(Education).where(Education.user_id == current_user.id)
    if education_id is not None:
        stmt = stmt.where(Education.id == education_id)

    result = await session.execute(stmt)
    rows = list(result.scalars().all())
    if not rows:
        raise NotFoundError("No education records found")

    for row in rows:
        await session.delete(row)
    await session.commit()
    return {"success": True, "message": "Education deleted"}
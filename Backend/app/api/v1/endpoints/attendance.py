from datetime import datetime

from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.attendance import Attendance
from app.models.user import UserRole
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceRead,
    attendance_to_response,
)

router = APIRouter(prefix="/attendance", tags=["attendance"])

HR_ROLES = (UserRole.super_admin, UserRole.hr_admin, UserRole.admin)


def _parse_dt(s: str | None):
    if not s:
        return None
    s = s.strip()
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.replace(tzinfo=None)
    except ValueError:
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


@router.get("", response_model=list[AttendanceRead])
async def list_attendance(session: DbSession, current_user: CurrentUser):
    """HR sees all; employee sees only their own."""
    stmt = select(Attendance).order_by(Attendance.punch_in.desc())
    if current_user.role not in HR_ROLES:
        stmt = stmt.where(Attendance.employee_id == current_user.employee_id)
    result = await session.execute(stmt)
    return [attendance_to_response(a) for a in result.scalars().all()]


@router.post("", response_model=AttendanceRead, status_code=status.HTTP_201_CREATED)
async def create_attendance(
    payload: AttendanceCreate,
    session: DbSession,
    current_user: CurrentUser,
):
    record = Attendance(
        user_id=current_user.id,
        employee_id=payload.employeeId or current_user.employee_id,
        employee_name=payload.employeeName or current_user.name,
        punch_in=_parse_dt(payload.punchIn),
        punch_out=_parse_dt(payload.punchOut),
        production_hours=payload.productionHours,
        production_minutes=payload.productionMinutes,
        production_seconds=payload.productionSeconds,
        break_hours=payload.breakHours,
        break_minutes=payload.breakMinutes,
        break_seconds=payload.breakSeconds,
        working_hours=payload.workingHours,
        working_minutes=payload.workingMinutes,
        working_seconds=payload.workingSeconds,
        overtime=payload.overtime,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return attendance_to_response(record)
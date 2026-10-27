# from datetime import date, datetime

# from fastapi import APIRouter, status
# from sqlalchemy import select

# from app.api.deps import CurrentUser, DbSession
# from app.exceptions import ConflictError, ForbiddenError, NotFoundError
# from app.models.leave import LeaveApplication, LeaveStatus, LeaveType, LeaveTypeName
# from app.models.user import User, UserRole
# from app.schemas.leave import (
#     LeaveApplicationCreate,
#     LeaveApplicationRead,
#     LeaveApplicationReview,
#     LeaveBalanceRead,
#     LeaveTypeRead,
#     LeaveTypeUpdate,
#     leave_to_response,
# )

# router = APIRouter(prefix="/leaves", tags=["leaves"])

# HR_ROLES = (UserRole.super_admin, UserRole.hr_admin, UserRole.admin)


# def _is_hr(user: User) -> bool:
#     return user.role in HR_ROLES


# def _days_between(from_d: date, to_d: date) -> float:
#     return float((to_d - from_d).days + 1)


# # ---------------- Leave Types (rules) ----------------

# @router.get("/types", response_model=list[LeaveTypeRead])
# async def list_leave_types(session: DbSession, _: CurrentUser):
#     result = await session.execute(select(LeaveType).order_by(LeaveType.id))
#     return list(result.scalars().all())


# @router.get("/types/{type_id}", response_model=LeaveTypeRead)
# async def get_leave_type(type_id: int, session: DbSession, _: CurrentUser):
#     record = await session.get(LeaveType, type_id)
#     if not record:
#         raise NotFoundError("Leave type not found")
#     return record


# @router.put("/types/{type_id}", response_model=LeaveTypeRead)
# async def update_leave_type(
#     type_id: int,
#     payload: LeaveTypeUpdate,
#     session: DbSession,
#     current_user: CurrentUser,
# ):
#     if not _is_hr(current_user):
#         raise ForbiddenError("Only HR can update leave rules")

#     record = await session.get(LeaveType, type_id)
#     if not record:
#         raise NotFoundError("Leave type not found")

#     for field, value in payload.model_dump(exclude_unset=True).items():
#         if value is not None:
#             setattr(record, field, value)

#     await session.commit()
#     await session.refresh(record)
#     return record


# # ---------------- Applications ----------------

# @router.post("/apply", response_model=LeaveApplicationRead, status_code=status.HTTP_201_CREATED)
# async def apply_leave(
#     payload: LeaveApplicationCreate,
#     session: DbSession,
#     current_user: CurrentUser,
# ):
#     if payload.to_date < payload.from_date:
#         raise ConflictError("End date cannot be before start date")

#     total_days = _days_between(payload.from_date, payload.to_date)

#     record = LeaveApplication(
#         user_id=current_user.id,
#         employee_id=current_user.employee_id,
#         employee_name=current_user.name,
#         leave_type=payload.leave_type,
#         from_date=payload.from_date,
#         to_date=payload.to_date,
#         total_days=total_days,
#         reason=payload.reason,
#         status=LeaveStatus.pending,
#     )
#     session.add(record)
#     await session.commit()
#     await session.refresh(record)
#     return leave_to_response(record)


# @router.get("/my", response_model=list[LeaveApplicationRead])
# async def my_leaves(session: DbSession, current_user: CurrentUser):
#     result = await session.execute(
#         select(LeaveApplication)
#         .where(LeaveApplication.user_id == current_user.id)
#         .order_by(LeaveApplication.applied_at.desc())
#     )
#     return [leave_to_response(a) for a in result.scalars().all()]


# @router.get("/all", response_model=list[LeaveApplicationRead])
# async def all_leaves(
#     session: DbSession,
#     current_user: CurrentUser,
#     status_filter: LeaveStatus | None = None,
# ):
#     if not _is_hr(current_user):
#         raise ForbiddenError("Only HR can view all leaves")

#     stmt = select(LeaveApplication).order_by(LeaveApplication.applied_at.desc())
#     if status_filter is not None:
#         stmt = stmt.where(LeaveApplication.status == status_filter)

#     result = await session.execute(stmt)
#     return [leave_to_response(a) for a in result.scalars().all()]


# @router.get("/{leave_id}", response_model=LeaveApplicationRead)
# async def get_leave(leave_id: int, session: DbSession, current_user: CurrentUser):
#     record = await session.get(LeaveApplication, leave_id)
#     if not record:
#         raise NotFoundError("Leave application not found")
#     if not _is_hr(current_user) and record.user_id != current_user.id:
#         raise ForbiddenError("You cannot view this leave application")
#     return leave_to_response(record)


# @router.post("/{leave_id}/approve", response_model=LeaveApplicationRead)
# async def approve_leave(
#     leave_id: int,
#     payload: LeaveApplicationReview,
#     session: DbSession,
#     current_user: CurrentUser,
# ):
#     if not _is_hr(current_user):
#         raise ForbiddenError("Only HR can approve leaves")

#     record = await session.get(LeaveApplication, leave_id)
#     if not record:
#         raise NotFoundError("Leave application not found")
#     if record.status != LeaveStatus.pending:
#         raise ConflictError(f"Cannot approve a {record.status.value} application")

#     record.status = LeaveStatus.approved
#     record.reviewed_by_id = current_user.id
#     record.reviewed_by_name = current_user.name
#     record.reviewed_at = datetime.utcnow()
#     record.review_comment = payload.comment

#     await session.commit()
#     await session.refresh(record)
#     return leave_to_response(record)


# @router.post("/{leave_id}/reject", response_model=LeaveApplicationRead)
# async def reject_leave(
#     leave_id: int,
#     payload: LeaveApplicationReview,
#     session: DbSession,
#     current_user: CurrentUser,
# ):
#     if not _is_hr(current_user):
#         raise ForbiddenError("Only HR can reject leaves")

#     record = await session.get(LeaveApplication, leave_id)
#     if not record:
#         raise NotFoundError("Leave application not found")
#     if record.status != LeaveStatus.pending:
#         raise ConflictError(f"Cannot reject a {record.status.value} application")

#     record.status = LeaveStatus.rejected
#     record.reviewed_by_id = current_user.id
#     record.reviewed_by_name = current_user.name
#     record.reviewed_at = datetime.utcnow()
#     record.review_comment = payload.comment

#     await session.commit()
#     await session.refresh(record)
#     return leave_to_response(record)


# @router.post("/{leave_id}/cancel", response_model=LeaveApplicationRead)
# async def cancel_leave(leave_id: int, session: DbSession, current_user: CurrentUser):
#     record = await session.get(LeaveApplication, leave_id)
#     if not record:
#         raise NotFoundError("Leave application not found")
#     if record.user_id != current_user.id and not _is_hr(current_user):
#         raise ForbiddenError("You cannot cancel this leave")
#     if record.status != LeaveStatus.pending:
#         raise ConflictError("Only pending leaves can be cancelled")

#     record.status = LeaveStatus.cancelled
#     await session.commit()
#     await session.refresh(record)
#     return leave_to_response(record)


# # ---------------- Balances ----------------

# def _compute_balance(user, apps, types_by_name):
#     used = {LeaveTypeName.casual: 0.0, LeaveTypeName.sick: 0.0, LeaveTypeName.earned: 0.0}
#     pending = {LeaveTypeName.casual: 0.0, LeaveTypeName.sick: 0.0, LeaveTypeName.earned: 0.0}
#     for a in apps:
#         if a.status == LeaveStatus.approved:
#             used[a.leave_type] = used.get(a.leave_type, 0) + float(a.total_days or 0)
#         elif a.status == LeaveStatus.pending:
#             pending[a.leave_type] = pending.get(a.leave_type, 0) + float(a.total_days or 0)

#     casual_alloc = types_by_name.get(LeaveTypeName.casual, 12)
#     sick_alloc = types_by_name.get(LeaveTypeName.sick, 12)
#     earned_alloc = types_by_name.get(LeaveTypeName.earned, 12)

#     return LeaveBalanceRead(
#         employeeId=user.employee_id,
#         employeeName=user.name,
#         casual=max(0.0, casual_alloc - used.get(LeaveTypeName.casual, 0)),
#         sick=max(0.0, sick_alloc - used.get(LeaveTypeName.sick, 0)),
#         earned=max(0.0, earned_alloc - used.get(LeaveTypeName.earned, 0)),
#         compOff=0,
#         totalAllocated=casual_alloc + sick_alloc + earned_alloc,
#         totalUsed=sum(used.values()),
#         totalPending=sum(pending.values()),
#     )


# @router.get("/balance/my", response_model=LeaveBalanceRead)
# async def my_balance(session: DbSession, current_user: CurrentUser):
#     types_res = await session.execute(select(LeaveType))
#     types_by_name = {t.name: t.leaves_per_year for t in types_res.scalars().all()}

#     apps_res = await session.execute(
#         select(LeaveApplication).where(LeaveApplication.user_id == current_user.id)
#     )
#     return _compute_balance(current_user, list(apps_res.scalars().all()), types_by_name)


# @router.get("/balance/all", response_model=list[LeaveBalanceRead])
# async def all_balances(session: DbSession, current_user: CurrentUser):
#     if not _is_hr(current_user):
#         raise ForbiddenError("Only HR can view all balances")

#     types_res = await session.execute(select(LeaveType))
#     types_by_name = {t.name: t.leaves_per_year for t in types_res.scalars().all()}

#     users_res = await session.execute(select(User).order_by(User.id))
#     users = list(users_res.scalars().all())

#     apps_res = await session.execute(select(LeaveApplication))
#     apps_by_user = {}
#     for a in apps_res.scalars().all():
#         apps_by_user.setdefault(a.user_id, []).append(a)

#     return [_compute_balance(u, apps_by_user.get(u.id, []), types_by_name) for u in users]







from datetime import date, datetime

from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.leave import LeaveApplication, LeaveStatus, LeaveType, LeaveTypeName
from app.models.user import User, UserRole
from app.schemas.leave import (
    LeaveApplicationCreate,
    LeaveApplicationRead,
    LeaveApplicationReview,
    LeaveBalanceRead,
    LeaveTypeRead,
    LeaveTypeUpdate,
    leave_to_response,
)

router = APIRouter(prefix="/leaves", tags=["leaves"])

HR_ROLES = (UserRole.super_admin, UserRole.hr_admin, UserRole.admin)


def _is_hr(user: User) -> bool:
    return user.role in HR_ROLES


def _days_between(from_d: date, to_d: date) -> float:
    return float((to_d - from_d).days + 1)


# ---------------- Leave Types (rules) ----------------

@router.get("/types", response_model=list[LeaveTypeRead])
async def list_leave_types(session: DbSession, _: CurrentUser):
    result = await session.execute(select(LeaveType).order_by(LeaveType.id))
    return list(result.scalars().all())


@router.get("/types/{type_id}", response_model=LeaveTypeRead)
async def get_leave_type(type_id: int, session: DbSession, _: CurrentUser):
    record = await session.get(LeaveType, type_id)
    if not record:
        raise NotFoundError("Leave type not found")
    return record


@router.put("/types/{type_id}", response_model=LeaveTypeRead)
async def update_leave_type(
    type_id: int,
    payload: LeaveTypeUpdate,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can update leave rules")

    record = await session.get(LeaveType, type_id)
    if not record:
        raise NotFoundError("Leave type not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(record, field, value)

    await session.commit()
    await session.refresh(record)
    return record


# ---------------- Applications ----------------

@router.post("/apply", response_model=LeaveApplicationRead, status_code=status.HTTP_201_CREATED)
async def apply_leave(
    payload: LeaveApplicationCreate,
    session: DbSession,
    current_user: CurrentUser,
):
    if payload.to_date < payload.from_date:
        raise ConflictError("End date cannot be before start date")

    total_days = _days_between(payload.from_date, payload.to_date)

    type_res = await session.execute(
        select(LeaveType).where(LeaveType.name == payload.leave_type)
    )
    leave_type = type_res.scalar_one_or_none()
    if not leave_type or not leave_type.is_active:
        raise ConflictError(
            f"Leave type '{payload.leave_type.value}' is not configured or inactive"
        )

    today = date.today()

    if payload.from_date < today:
        if not leave_type.backdated_allowed:
            raise ConflictError(f"{leave_type.display_name} cannot be backdated")
        days_ago = (today - payload.from_date).days
        if days_ago > leave_type.backdated_up_to_days:
            raise ConflictError(
                f"{leave_type.display_name} can only be backdated up to "
                f"{leave_type.backdated_up_to_days} day(s)"
            )
    if payload.from_date > today and not leave_type.future_dated_allowed:
        raise ConflictError(f"{leave_type.display_name} cannot be future-dated")

    half_day = (payload.half_day or "").strip()
    is_half = half_day and half_day.lower() not in ("", "full day")
    if is_half and payload.from_date != payload.to_date:
        raise ConflictError("Half-day leave must be for a single day")
    if is_half:
        total_days = 0.5

    if total_days > leave_type.continuous_leaves_allowed:
        raise ConflictError(
            f"{leave_type.display_name} allows a maximum of "
            f"{leave_type.continuous_leaves_allowed} continuous day(s)"
        )

    overlap_res = await session.execute(
        select(LeaveApplication).where(
            LeaveApplication.user_id == current_user.id,
            LeaveApplication.status.in_([LeaveStatus.pending, LeaveStatus.approved]),
            LeaveApplication.from_date <= payload.to_date,
            LeaveApplication.to_date >= payload.from_date,
        )
    )
    if overlap_res.scalars().first():
        raise ConflictError(
            "You already have a pending/approved leave overlapping these dates"
        )

    month_start = payload.from_date.replace(day=1)
    month_end = (
        date(month_start.year + 1, 1, 1)
        if month_start.month == 12
        else date(month_start.year, month_start.month + 1, 1)
    )
    month_res = await session.execute(
        select(LeaveApplication).where(
            LeaveApplication.user_id == current_user.id,
            LeaveApplication.leave_type == payload.leave_type,
            LeaveApplication.status.in_([LeaveStatus.pending, LeaveStatus.approved]),
            LeaveApplication.from_date >= month_start,
            LeaveApplication.from_date < month_end,
        )
    )
    month_days = sum(float(a.total_days or 0) for a in month_res.scalars().all())
    if (
        leave_type.max_leaves_per_month
        and month_days + total_days > leave_type.max_leaves_per_month
    ):
        raise ConflictError(
            f"Monthly limit of {leave_type.max_leaves_per_month:g} day(s) for "
            f"{leave_type.display_name} exceeded "
            f"(already requested {month_days:g} in this month)"
        )

    apps_res = await session.execute(
        select(LeaveApplication).where(LeaveApplication.user_id == current_user.id)
    )
    used = 0.0
    pending = 0.0
    for a in apps_res.scalars().all():
        if a.leave_type != payload.leave_type:
            continue
        if a.status == LeaveStatus.approved:
            used += float(a.total_days or 0)
        elif a.status == LeaveStatus.pending:
            pending += float(a.total_days or 0)

    available = float(leave_type.leaves_per_year) - used - pending
    if not leave_type.negative_leaves_allowed and total_days > available:
        raise ConflictError(
            f"Insufficient {leave_type.display_name} balance. "
            f"Available: {available:g} day(s), Requested: {total_days:g} day(s)"
        )

    record = LeaveApplication(
        user_id=current_user.id,
        employee_id=current_user.employee_id,
        employee_name=current_user.name,
        leave_type=payload.leave_type,
        from_date=payload.from_date,
        to_date=payload.to_date,
        total_days=total_days,
        half_day=half_day or None,
        reason=payload.reason,
        status=LeaveStatus.pending,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return leave_to_response(record)


@router.get("/my", response_model=list[LeaveApplicationRead])
async def my_leaves(session: DbSession, current_user: CurrentUser):
    result = await session.execute(
        select(LeaveApplication)
        .where(LeaveApplication.user_id == current_user.id)
        .order_by(LeaveApplication.applied_at.desc())
    )
    return [leave_to_response(a) for a in result.scalars().all()]


@router.get("/all", response_model=list[LeaveApplicationRead])
async def all_leaves(
    session: DbSession,
    current_user: CurrentUser,
    status_filter: LeaveStatus | None = None,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can view all leaves")

    stmt = select(LeaveApplication).order_by(LeaveApplication.applied_at.desc())
    if status_filter is not None:
        stmt = stmt.where(LeaveApplication.status == status_filter)

    result = await session.execute(stmt)
    return [leave_to_response(a) for a in result.scalars().all()]


@router.get("/{leave_id}", response_model=LeaveApplicationRead)
async def get_leave(leave_id: int, session: DbSession, current_user: CurrentUser):
    record = await session.get(LeaveApplication, leave_id)
    if not record:
        raise NotFoundError("Leave application not found")
    if not _is_hr(current_user) and record.user_id != current_user.id:
        raise ForbiddenError("You cannot view this leave application")
    return leave_to_response(record)


@router.post("/{leave_id}/approve", response_model=LeaveApplicationRead)
async def approve_leave(
    leave_id: int,
    payload: LeaveApplicationReview,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can approve leaves")

    record = await session.get(LeaveApplication, leave_id)
    if not record:
        raise NotFoundError("Leave application not found")
    if record.status != LeaveStatus.pending:
        raise ConflictError(f"Cannot approve a {record.status.value} application")

    record.status = LeaveStatus.approved
    record.reviewed_by_id = current_user.id
    record.reviewed_by_name = current_user.name
    record.reviewed_at = datetime.utcnow()
    record.review_comment = payload.comment

    await session.commit()
    await session.refresh(record)
    return leave_to_response(record)


@router.post("/{leave_id}/reject", response_model=LeaveApplicationRead)
async def reject_leave(
    leave_id: int,
    payload: LeaveApplicationReview,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can reject leaves")

    record = await session.get(LeaveApplication, leave_id)
    if not record:
        raise NotFoundError("Leave application not found")
    if record.status != LeaveStatus.pending:
        raise ConflictError(f"Cannot reject a {record.status.value} application")

    record.status = LeaveStatus.rejected
    record.reviewed_by_id = current_user.id
    record.reviewed_by_name = current_user.name
    record.reviewed_at = datetime.utcnow()
    record.review_comment = payload.comment

    await session.commit()
    await session.refresh(record)
    return leave_to_response(record)


@router.post("/{leave_id}/cancel", response_model=LeaveApplicationRead)
async def cancel_leave(leave_id: int, session: DbSession, current_user: CurrentUser):
    record = await session.get(LeaveApplication, leave_id)
    if not record:
        raise NotFoundError("Leave application not found")
    if record.user_id != current_user.id and not _is_hr(current_user):
        raise ForbiddenError("You cannot cancel this leave")
    if record.status != LeaveStatus.pending:
        raise ConflictError("Only pending leaves can be cancelled")

    record.status = LeaveStatus.cancelled
    await session.commit()
    await session.refresh(record)
    return leave_to_response(record)


# ---------------- Balances ----------------

def _compute_balance(user, apps, types_by_name):
    used = {}
    pending = {}
    rejected = {}
    for a in apps:
        t = a.leave_type
        days = float(a.total_days or 0)
        if a.status == LeaveStatus.approved:
            used[t] = used.get(t, 0) + days
        elif a.status == LeaveStatus.pending:
            pending[t] = pending.get(t, 0) + days
        elif a.status == LeaveStatus.rejected:
            rejected[t] = rejected.get(t, 0) + days

    casual_alloc = float(types_by_name.get(LeaveTypeName.casual, 12))
    sick_alloc   = float(types_by_name.get(LeaveTypeName.sick, 12))
    earned_alloc = float(types_by_name.get(LeaveTypeName.earned, 12))

    cu = used.get(LeaveTypeName.casual, 0.0)
    cp = pending.get(LeaveTypeName.casual, 0.0)
    cr = rejected.get(LeaveTypeName.casual, 0.0)
    su = used.get(LeaveTypeName.sick, 0.0)
    sp = pending.get(LeaveTypeName.sick, 0.0)
    sr = rejected.get(LeaveTypeName.sick, 0.0)
    eu = used.get(LeaveTypeName.earned, 0.0)
    ep = pending.get(LeaveTypeName.earned, 0.0)
    er = rejected.get(LeaveTypeName.earned, 0.0)

    return LeaveBalanceRead(
        employeeId=user.employee_id,
        employeeName=user.name,
        casual=max(0.0, casual_alloc - cu - cp),
        sick=max(0.0, sick_alloc - su - sp),
        earned=max(0.0, earned_alloc - eu - ep),
        compOff=0,
        casualAllocated=casual_alloc, casualUsed=cu, casualPending=cp, casualRejected=cr,
        sickAllocated=sick_alloc,     sickUsed=su,   sickPending=sp,   sickRejected=sr,
        earnedAllocated=earned_alloc, earnedUsed=eu, earnedPending=ep, earnedRejected=er,
        totalAllocated=casual_alloc + sick_alloc + earned_alloc,
        totalUsed=cu + su + eu,
        totalPending=cp + sp + ep,
        totalRejected=cr + sr + er,
    )


@router.get("/balance/my", response_model=LeaveBalanceRead)
async def my_balance(session: DbSession, current_user: CurrentUser):
    types_res = await session.execute(select(LeaveType))
    types_by_name = {t.name: t.leaves_per_year for t in types_res.scalars().all()}

    apps_res = await session.execute(
        select(LeaveApplication).where(LeaveApplication.user_id == current_user.id)
    )
    return _compute_balance(current_user, list(apps_res.scalars().all()), types_by_name)


@router.get("/balance/all", response_model=list[LeaveBalanceRead])
async def all_balances(session: DbSession, current_user: CurrentUser):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can view all balances")

    types_res = await session.execute(select(LeaveType))
    types_by_name = {t.name: t.leaves_per_year for t in types_res.scalars().all()}

    users_res = await session.execute(select(User).order_by(User.id))
    users = list(users_res.scalars().all())

    apps_res = await session.execute(select(LeaveApplication))
    apps_by_user = {}
    for a in apps_res.scalars().all():
        apps_by_user.setdefault(a.user_id, []).append(a)

    return [_compute_balance(u, apps_by_user.get(u.id, []), types_by_name) for u in users]
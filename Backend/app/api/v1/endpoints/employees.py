# from fastapi import APIRouter, status
# from sqlalchemy import or_, select

# from app.api.deps import CurrentUser, DbSession
# from app.core.security import hash_password
# from app.exceptions import ConflictError, ForbiddenError, NotFoundError
# from app.models.user import User, UserRole
# from app.repositories.user_repository import UserRepository
# from app.schemas.employee import (
#     EmployeeCreate,
#     EmployeeRead,
#     EmployeeUpdate,
#     user_to_response,
# )

# router = APIRouter(prefix="/employee", tags=["employee"])

# HR_ROLES = (UserRole.super_admin, UserRole.hr_admin, UserRole.admin)


# def _role_prefix(role: UserRole) -> str:
#     return {
#         UserRole.super_admin: "SA",
#         UserRole.hr_admin: "HR",
#         UserRole.admin: "ADM",
#         UserRole.manager: "MGR",
#         UserRole.employee: "EMP",
#     }[role]


# def _auto_password() -> str:
#     import secrets
#     import string

#     alphabet = string.ascii_letters + string.digits
#     return "".join(secrets.choice(alphabet) for _ in range(10)) + "@1Aa"


# async def _resolve_employee(session, employee_id: str) -> User:
#     stmt = select(User)
#     if str(employee_id).isdigit():
#         stmt = stmt.where(
#             or_(User.id == int(employee_id), User.employee_id == employee_id)
#         )
#     else:
#         stmt = stmt.where(User.employee_id == employee_id)

#     result = await session.execute(stmt)
#     user = result.scalar_one_or_none()
#     if not user:
#         raise NotFoundError(f"Employee {employee_id} not found")
#     return user


# @router.get("/getAllEmployee", response_model=list[EmployeeRead])
# async def get_all_employees(session: DbSession, _: CurrentUser):
#     result = await session.execute(select(User).order_by(User.id))
#     return [user_to_response(u) for u in result.scalars().all()]


# @router.post(
#     "/register",
#     response_model=EmployeeRead,
#     status_code=status.HTTP_201_CREATED,
# )
# async def register_employee(
#     data: EmployeeCreate,
#     session: DbSession,
#     current_user: CurrentUser,
# ):
#     if current_user.role not in HR_ROLES:
#         raise ForbiddenError("Only HR/Admin/Super Admin can add employees")

#     resolved_name = data.resolved_name
#     if not resolved_name:
#         raise ConflictError("Name is required")

#     repo = UserRepository(session)

#     if await repo.get_by_email(str(data.email).lower().strip()):
#         raise ConflictError("Email already registered")

#     if data.employee_id:
#         existing = await session.execute(
#             select(User).where(User.employee_id == data.employee_id)
#         )
#         if existing.scalar_one_or_none():
#             raise ConflictError(f"Employee ID {data.employee_id} already exists")

#     password = data.password or _auto_password()

#     user = await repo.create(
#         name=resolved_name,
#         email=str(data.email).lower().strip(),
#         hashed_password=hash_password(password),
#         role=data.role,
#         employee_id=data.employee_id or None,
#         date_of_joining=data.date_of_joining,
#         date_of_birth=data.date_of_birth,
#         contact_no=data.contact_no,
#         blood_group=data.blood_group,
#         personal_mail_id=data.personal_mail_id,
#         designation=data.designation,
#         pan_number=data.pan_number,
#         aadhar_card_number=data.aadhar_card_number,
#         is_active=True,
#     )

#     if not user.employee_id:
#         user.employee_id = f"{_role_prefix(user.role)}{user.id:05d}"
#         await session.flush()
#         await session.refresh(user)

#     await session.commit()
#     await session.refresh(user)
#     return user_to_response(user)


# @router.put("/update/{employee_id}", response_model=EmployeeRead)
# async def update_employee(
#     employee_id: str,
#     data: EmployeeUpdate,
#     session: DbSession,
#     current_user: CurrentUser,
# ):
#     if current_user.role not in HR_ROLES:
#         raise ForbiddenError("Only HR/Admin/Super Admin can update employees")

#     user = await _resolve_employee(session, employee_id)

#     if name := data.resolved_name:
#         user.name = name

#     if data.email:
#         new_email = str(data.email).lower().strip()
#         existing = await session.execute(
#             select(User).where(User.email == new_email, User.id != user.id)
#         )
#         if existing.scalar_one_or_none():
#             raise ConflictError("Email already used by another user")
#         user.email = new_email

#     if data.role is not None:
#         user.role = data.role
#     if data.date_of_joining is not None:
#         user.date_of_joining = data.date_of_joining
#     if data.date_of_birth is not None:
#         user.date_of_birth = data.date_of_birth
#     if data.contact_no is not None:
#         user.contact_no = data.contact_no
#     if data.blood_group is not None:
#         user.blood_group = data.blood_group
#     if data.personal_mail_id is not None:
#         user.personal_mail_id = data.personal_mail_id
#     if data.designation is not None:
#         user.designation = data.designation
#     if data.pan_number is not None:
#         user.pan_number = data.pan_number
#     if data.aadhar_card_number is not None:
#         user.aadhar_card_number = data.aadhar_card_number
#     if data.password:
#         user.hashed_password = hash_password(data.password)

#     await session.commit()
#     await session.refresh(user)
#     return user_to_response(user)


# @router.delete("/delete/{employee_id}")
# async def delete_employee(
#     employee_id: str,
#     session: DbSession,
#     current_user: CurrentUser,
# ):
#     if current_user.role not in HR_ROLES:
#         raise ForbiddenError("Only HR/Admin/Super Admin can delete employees")

#     user = await _resolve_employee(session, employee_id)

#     if user.role == UserRole.super_admin:
#         raise ForbiddenError("Cannot delete a super admin")
#     if user.id == current_user.id:
#         raise ForbiddenError("You cannot delete your own account")

#     await session.delete(user)
#     await session.commit()
#     return {"success": True, "message": "Employee deleted"}


from fastapi import APIRouter, status
from pydantic import BaseModel as _BaseModel
from sqlalchemy import or_, select

from app.api.deps import CurrentUser, DbSession
from app.core.security import hash_password, verify_password
from app.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeRead,
    EmployeeUpdate,
    user_to_response,
)

router = APIRouter(prefix="/employee", tags=["employee"])

HR_ROLES = (UserRole.super_admin, UserRole.hr_admin, UserRole.admin)


def _role_prefix(role: UserRole) -> str:
    return {
        UserRole.super_admin: "SA",
        UserRole.hr_admin: "HR",
        UserRole.admin: "ADM",
        UserRole.manager: "MGR",
        UserRole.employee: "EMP",
    }[role]


def _auto_password() -> str:
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(10)) + "@1Aa"


async def _resolve_employee(session, employee_id: str) -> User:
    stmt = select(User)
    if str(employee_id).isdigit():
        stmt = stmt.where(
            or_(User.id == int(employee_id), User.employee_id == employee_id)
        )
    else:
        stmt = stmt.where(User.employee_id == employee_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError(f"Employee {employee_id} not found")
    return user


@router.get("/getAllEmployee", response_model=list[EmployeeRead])
async def get_all_employees(session: DbSession, _: CurrentUser):
    result = await session.execute(select(User).order_by(User.id))
    return [user_to_response(u) for u in result.scalars().all()]


@router.post(
    "/register",
    response_model=EmployeeRead,
    status_code=status.HTTP_201_CREATED,
)
async def register_employee(
    data: EmployeeCreate,
    session: DbSession,
    current_user: CurrentUser,
):
    if current_user.role not in HR_ROLES:
        raise ForbiddenError("Only HR/Admin/Super Admin can add employees")

    resolved_name = data.resolved_name
    if not resolved_name:
        raise ConflictError("Name is required")

    repo = UserRepository(session)

    if await repo.get_by_email(str(data.email).lower().strip()):
        raise ConflictError("Email already registered")

    if data.employee_id:
        existing = await session.execute(
            select(User).where(User.employee_id == data.employee_id)
        )
        if existing.scalar_one_or_none():
            raise ConflictError(f"Employee ID {data.employee_id} already exists")

    password = data.password or _auto_password()
    user = await repo.create(
        name=resolved_name,
        email=str(data.email).lower().strip(),
        hashed_password=hash_password(password),
        role=data.role,
        employee_id=data.employee_id or None,
        date_of_joining=data.date_of_joining,
        date_of_birth=data.date_of_birth,
        contact_no=data.contact_no,
        alternate_phone=data.alternate_phone,
        blood_group=data.blood_group,
        personal_mail_id=data.personal_mail_id,
        designation=data.designation,
        pan_number=data.pan_number,
        aadhar_card_number=data.aadhar_card_number,
        is_active=True,
    )

    if not user.employee_id:
        user.employee_id = f"{_role_prefix(user.role)}{user.id:05d}"
        await session.flush()
        await session.refresh(user)

    await session.commit()
    await session.refresh(user)
    return user_to_response(user)


@router.put("/update/{employee_id}", response_model=EmployeeRead)
async def update_employee(
    employee_id: str,
    data: EmployeeUpdate,
    session: DbSession,
    current_user: CurrentUser,
):
    user = await _resolve_employee(session, employee_id)

    is_self = user.id == current_user.id
    if not is_self and current_user.role not in HR_ROLES:
        raise ForbiddenError("Not enough permissions")

    if data.role is not None and current_user.role not in HR_ROLES:
        raise ForbiddenError("Only HR can change role")

    if name := data.resolved_name:
        user.name = name

    if data.email:
        new_email = str(data.email).lower().strip()
        if current_user.role not in HR_ROLES and new_email != user.email:
            raise ForbiddenError("Only HR can change email")
        existing = await session.execute(
            select(User).where(User.email == new_email, User.id != user.id)
        )
        if existing.scalar_one_or_none():
            raise ConflictError("Email already used by another user")
        user.email = new_email

    if data.role is not None:
        user.role = data.role
    if data.date_of_joining is not None:
        user.date_of_joining = data.date_of_joining
    if data.date_of_birth is not None:
        user.date_of_birth = data.date_of_birth
    if data.contact_no is not None:
        user.contact_no = data.contact_no
    if data.alternate_phone is not None:
        user.alternate_phone = data.alternate_phone
    if data.blood_group is not None:
        user.blood_group = data.blood_group
    if data.personal_mail_id is not None:
        user.personal_mail_id = data.personal_mail_id
    if data.designation is not None:
        user.designation = data.designation
    if data.pan_number is not None:
        user.pan_number = data.pan_number
    if data.aadhar_card_number is not None:
        user.aadhar_card_number = data.aadhar_card_number
    if data.password:
        user.hashed_password = hash_password(data.password)

    await session.commit()
    await session.refresh(user)
    return user_to_response(user)


@router.delete("/delete/{employee_id}")
async def delete_employee(
    employee_id: str,
    session: DbSession,
    current_user: CurrentUser,
):
    if current_user.role not in HR_ROLES:
        raise ForbiddenError("Only HR/Admin/Super Admin can delete employees")
    user = await _resolve_employee(session, employee_id)
    if user.role == UserRole.super_admin:
        raise ForbiddenError("Cannot delete a super admin")
    if user.id == current_user.id:
        raise ForbiddenError("You cannot delete your own account")
    await session.delete(user)
    await session.commit()
    return {"success": True, "message": "Employee deleted"}


class _PasswordChange(_BaseModel):
    currentPassword: str
    newPassword: str
    confirmPassword: str | None = None


@router.put("/password/{email}")
async def update_password(
    email: str,
    data: _PasswordChange,
    session: DbSession,
    current_user: CurrentUser,
):
    repo = UserRepository(session)
    user = await repo.get_by_email(email.lower().strip())
    if not user:
        raise NotFoundError("User not found")

    is_self = user.id == current_user.id
    is_hr = current_user.role in HR_ROLES
    if not (is_self or is_hr):
        raise ForbiddenError("You cannot change this user's password")

    if is_self and not verify_password(data.currentPassword, user.hashed_password):
        raise UnauthorizedError("Current password is incorrect")

    if data.confirmPassword and data.confirmPassword != data.newPassword:
        raise ConflictError("New passwords do not match")

    user.hashed_password = hash_password(data.newPassword)
    await session.commit()
    return "password updated successfully"
from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession, OptionalUser, UserServiceDep
from app.core.security import create_access_token, hash_password, verify_password
from app.exceptions import UnauthorizedError
from app.schemas.common import MessageResponse, SuccessResponse
from app.schemas.user import (
    LoginResponse,
    ProfileUpdate,
    RegisterResponse,
    UserLogin,
    UserRead,
    UserRegister,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _enrich(user) -> dict:
    full = (user.name or "").strip()
    first, _, last = full.partition(" ")
    return {
        "id": user.id,
        "name": full,
        "email": user.email,
        "role": user.role,
        "employee_id": user.employee_id,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "employeeId": user.employee_id,
        "firstName": first or "",
        "lastName": last or "",
        "designation": user.designation,
        "blood_group": user.blood_group,
        "bloodGroup": user.blood_group,
        "contact_no": user.contact_no,
        "phoneNumber": user.contact_no,
        "alternate_phone": user.alternate_phone,
        "alternatePhoneNumber": user.alternate_phone,
        "personal_mail_id": user.personal_mail_id,
        "personalEmail": user.personal_mail_id,
        "officialEmail": user.email,
        "date_of_joining": user.date_of_joining,
        "joinDate": user.date_of_joining,
        "date_of_birth": user.date_of_birth,
        "dob": user.date_of_birth,
        "pan_number": user.pan_number,
        "panNumber": user.pan_number,
        "aadhar_card_number": user.aadhar_card_number,
        "aadharCardNumber": user.aadhar_card_number,
        "profile_image": user.profile_image,
        "profileImage": user.profile_image,
    }


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserRegister,
    service: UserServiceDep,
    current_user: OptionalUser,
    session: DbSession,
):
    user = await service.register(data, current_user)
    await session.commit()
    await session.refresh(user)
    return RegisterResponse(data=_enrich(user))


@router.post("/login", response_model=LoginResponse)
async def login(data: UserLogin, service: UserServiceDep):
    user = await service.authenticate(data.email, data.password)
    token = create_access_token(user.id)
    return LoginResponse(token=token, user=_enrich(user))


@router.get("/profile", response_model=SuccessResponse[dict])
async def get_profile(user: CurrentUser):
    return SuccessResponse(data=_enrich(user))


@router.put("/profile", response_model=SuccessResponse[dict])
async def update_profile(data: ProfileUpdate, user: CurrentUser, session: DbSession):
    if data.name is not None:
        user.name = data.name.strip()

    field_map = {
        "personal_mail_id": data.personal_mail_id or data.personalEmail,
        "contact_no": data.contact_no or data.phoneNumber,
        "alternate_phone": data.alternate_phone or data.alternatePhoneNumber,
        "blood_group": data.blood_group or data.bloodGroup,
        "date_of_birth": data.date_of_birth or data.dob,
        "designation": data.designation,
        "pan_number": data.pan_number or data.panNumber,
        "aadhar_card_number": data.aadhar_card_number or data.aadharCardNumber,
        "profile_image": data.profile_image or data.profileImage,
    }
    for field, value in field_map.items():
        if value is not None:
            setattr(user, field, value)

    await session.commit()
    await session.refresh(user)
    return SuccessResponse(data=_enrich(user), message="Profile updated")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    currentPassword: str,
    newPassword: str,
    user: CurrentUser,
    session: DbSession,
):
    if not verify_password(currentPassword, user.hashed_password):
        raise UnauthorizedError("Current password is incorrect")
    user.hashed_password = hash_password(newPassword)
    await session.commit()
    return MessageResponse(message="password updated successfully")


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser):
    return _enrich(user)


@router.get("/all-users", response_model=SuccessResponse[list[UserRead]])
async def all_users(_: CurrentUser, service: UserServiceDep):
    users = await service.list_users()
    return SuccessResponse(data=[_enrich(u) for u in users])


@router.post("/logout", response_model=MessageResponse)
async def logout(_: CurrentUser):
    return MessageResponse(message="Logged out")
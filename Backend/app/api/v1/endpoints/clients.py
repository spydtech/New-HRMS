from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.client import Client
from app.models.user import UserRole
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate

router = APIRouter(prefix="/clients", tags=["clients"])

HR_ROLES = (UserRole.super_admin, UserRole.hr_admin, UserRole.admin)


def _is_hr(user) -> bool:
    return user.role in HR_ROLES


@router.get("", response_model=list[ClientRead])
async def list_clients(session: DbSession, _: CurrentUser):
    result = await session.execute(select(Client).order_by(Client.name))
    return list(result.scalars().all())


@router.get("/{client_id}", response_model=ClientRead)
async def get_client(client_id: int, session: DbSession, _: CurrentUser):
    client = await session.get(Client, client_id)
    if not client:
        raise NotFoundError("Client not found")
    return client


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: ClientCreate,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can create clients")

    email = str(payload.email).lower().strip()
    existing = await session.execute(select(Client).where(Client.email == email))
    if existing.scalar_one_or_none():
        raise ConflictError("A client with this email already exists")

    client = Client(
        name=payload.name.strip(),
        email=email,
        mobile=payload.mobile,
        company=payload.company,
        designation=payload.designation,
        status=payload.status or "User",
        address=payload.address,
        notes=payload.notes,
        profile_image=payload.profile_image,
        is_active=payload.is_active,
    )
    session.add(client)
    await session.commit()
    await session.refresh(client)
    return client


@router.put("/{client_id}", response_model=ClientRead)
async def update_client(
    client_id: int,
    payload: ClientUpdate,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can update clients")

    client = await session.get(Client, client_id)
    if not client:
        raise NotFoundError("Client not found")

    data = payload.model_dump(exclude_unset=True, by_alias=False)

    if "email" in data and data["email"]:
        new_email = str(data["email"]).lower().strip()
        if new_email != client.email:
            existing = await session.execute(
                select(Client).where(
                    Client.email == new_email, Client.id != client_id
                )
            )
            if existing.scalar_one_or_none():
                raise ConflictError("Email already used by another client")
            client.email = new_email

    for field in (
        "name", "mobile", "company", "designation", "status",
        "address", "notes", "profile_image", "is_active",
    ):
        if field in data:
            setattr(client, field, data[field])

    await session.commit()
    await session.refresh(client)
    return client


@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    session: DbSession,
    current_user: CurrentUser,
):
    if not _is_hr(current_user):
        raise ForbiddenError("Only HR can delete clients")

    client = await session.get(Client, client_id)
    if not client:
        raise NotFoundError("Client not found")

    await session.delete(client)
    await session.commit()
    return {"success": True, "message": "Client deleted"}
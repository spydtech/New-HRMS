from app.core.security import hash_password, verify_password
from app.exceptions import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRegister


# Who can register whom
ROLE_HIERARCHY: dict[UserRole, list[UserRole]] = {
    UserRole.super_admin: [
        UserRole.super_admin,
        UserRole.hr_admin,
        UserRole.admin,
        UserRole.employee,
    ],
    UserRole.hr_admin: [UserRole.employee],
    UserRole.admin: [UserRole.employee],
    UserRole.employee: [],
}

ROLE_PREFIX = {
    UserRole.super_admin: "SA",
    UserRole.hr_admin: "HR",
    UserRole.admin: "ADM",
    UserRole.employee: "EMP-SDT",
}


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def register(
        self,
        data: UserRegister,
        current_user: User | None,
    ) -> User:
        # 1. Email must be unique
        if await self.repo.get_by_email(data.email):
            raise ConflictError("Email already registered")

        # 2. Role permission check
        if current_user is None:
            # Public registration → employee only
            if data.role != UserRole.employee:
                raise ForbiddenError(
                    "Public registration is only allowed for 'employee' role"
                )
        else:
            allowed = ROLE_HIERARCHY.get(current_user.role, [])
            if data.role not in allowed:
                raise ForbiddenError(
                    f"You don't have permission to register '{data.role.value}' role"
                )

        # 3. Create user
        user = await self.repo.create(
            name=data.name.strip(),
            email=data.email.lower().strip(),
            hashed_password=hash_password(data.password),
            role=data.role,
            is_active=True,
        )

        # 4. Generate employee_id from DB id
        prefix = ROLE_PREFIX[data.role]
        user.employee_id = f"{prefix}{user.id:05d}"
        await self.repo.session.flush()
        await self.repo.session.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.repo.get_by_email(email.lower().strip())
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Incorrect email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is disabled. Contact your administrator.")
        return user

    async def get_or_404(self, user_id: int) -> User:
        user = await self.repo.get(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    async def list_users(self, offset: int = 0, limit: int = 100) -> list[User]:
        return await self.repo.list(offset=offset, limit=limit)
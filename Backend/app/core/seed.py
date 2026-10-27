# import logging

# from sqlalchemy import select

# from app.core.config import settings
# from app.core.security import hash_password
# from app.db.session import SessionLocal
# from app.models.leave import LeaveType, LeaveTypeName
# from app.models.user import UserRole
# from app.repositories.user_repository import UserRepository

# logger = logging.getLogger(__name__)


# DEFAULT_LEAVE_TYPES = [
#     {
#         "name": LeaveTypeName.casual,
#         "display_name": "Casual Leave",
#         "description": "This is a Default Description for the Leave Type. You can customize this",
#         "leaves_per_year": 12.0,
#         "weekends_between_leave": False,
#         "holidays_between_leave": False,
#         "accrual_enabled": True,
#         "accrual_frequency": "monthly",
#         "accrual_period": "No",
#         "allowed_under_probation": False,
#         "allowed_under_notice_period": False,
#         "encashment_allowed": True,
#         "max_encashment_days": 15,
#         "carry_forward_allowed": True,
#         "carry_forward_limit": 15,
#         "max_leaves_per_month": 1.0,
#         "continuous_leaves_allowed": 1,
#         "negative_leaves_allowed": False,
#         "future_dated_allowed": True,
#         "future_dated_after_days": 0,
#         "backdated_allowed": True,
#         "backdated_up_to_days": 15,
#         "next_year_till_month": "January",
#     },
#     {
#         "name": LeaveTypeName.sick,
#         "display_name": "Sick Leave",
#         "description": "This is a Default Description for the Leave Type. You can customize this",
#         "leaves_per_year": 12.0,
#         "weekends_between_leave": False,
#         "holidays_between_leave": False,
#         "accrual_enabled": True,
#         "accrual_frequency": "monthly",
#         "accrual_period": "No",
#         "allowed_under_probation": False,
#         "allowed_under_notice_period": False,
#         "encashment_allowed": True,
#         "max_encashment_days": 15,
#         "carry_forward_allowed": True,
#         "carry_forward_limit": 15,
#         "max_leaves_per_month": 1.0,
#         "continuous_leaves_allowed": 1,
#         "negative_leaves_allowed": False,
#         "future_dated_allowed": True,
#         "future_dated_after_days": 0,
#         "backdated_allowed": True,
#         "backdated_up_to_days": 15,
#         "next_year_till_month": "January",
#     },
#     {
#         "name": LeaveTypeName.earned,
#         "display_name": "Earned Leave",
#         "description": "This is a Default Description for the Leave Type. You can customize this",
#         "leaves_per_year": 12.0,
#         "weekends_between_leave": False,
#         "holidays_between_leave": False,
#         "accrual_enabled": True,
#         "accrual_frequency": "monthly",
#         "accrual_period": "No",
#         "allowed_under_probation": False,
#         "allowed_under_notice_period": False,
#         "encashment_allowed": True,
#         "max_encashment_days": 15,
#         "carry_forward_allowed": True,
#         "carry_forward_limit": 15,
#         "max_leaves_per_month": 1.0,
#         "continuous_leaves_allowed": 1,
#         "negative_leaves_allowed": False,
#         "future_dated_allowed": True,
#         "future_dated_after_days": 0,
#         "backdated_allowed": True,
#         "backdated_up_to_days": 15,
#         "next_year_till_month": "January",
#     },
# ]


# async def seed_super_admin() -> None:
#     async with SessionLocal() as session:
#         repo = UserRepository(session)
#         existing = await repo.get_by_email(settings.SUPER_ADMIN_EMAIL)
#         if existing:
#             logger.info("Super admin already exists: %s", existing.email)
#             return

#         user = await repo.create(
#             name=settings.SUPER_ADMIN_NAME,
#             email=settings.SUPER_ADMIN_EMAIL,
#             hashed_password=hash_password(settings.SUPER_ADMIN_PASSWORD),
#             role=UserRole.super_admin,
#             is_active=True,
#         )
#         user.employee_id = f"SA{user.id:05d}"
#         await session.commit()
#         logger.warning(
#             "✅ Super admin created → email=%s password=%s",
#             settings.SUPER_ADMIN_EMAIL,
#             settings.SUPER_ADMIN_PASSWORD,
#         )


# async def seed_leave_types() -> None:
#     async with SessionLocal() as session:
#         for cfg in DEFAULT_LEAVE_TYPES:
#             existing = await session.execute(
#                 select(LeaveType).where(LeaveType.name == cfg["name"])
#             )
#             if existing.scalar_one_or_none():
#                 logger.info("Leave type already exists: %s", cfg["name"].value)
#                 continue

#             session.add(LeaveType(**cfg))
#             logger.info("Seeded leave type: %s", cfg["name"].value)

#         await session.commit()




# app/core/seed.py
import logging

from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.leave import LeaveType, LeaveTypeName
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


DEFAULT_LEAVE_TYPES = [
    {
        "name": LeaveTypeName.casual,
        "display_name": "Casual Leave",
        "description": "This is a Default Description for the Leave Type. You can customize this",
        "leaves_per_year": 12.0,
        "weekends_between_leave": False,
        "holidays_between_leave": False,
        "accrual_enabled": True,
        "accrual_frequency": "monthly",
        "accrual_period": "No",
        "allowed_under_probation": False,
        "allowed_under_notice_period": False,
        "encashment_allowed": True,
        "max_encashment_days": 15,
        "carry_forward_allowed": True,
        "carry_forward_limit": 15,
        "max_leaves_per_month": 12.0,
        "continuous_leaves_allowed": 12,
        "negative_leaves_allowed": False,
        "future_dated_allowed": True,
        "future_dated_after_days": 0,
        "backdated_allowed": True,
        "backdated_up_to_days": 15,
        "next_year_till_month": "January",
    },
    {
        "name": LeaveTypeName.sick,
        "display_name": "Sick Leave",
        "description": "This is a Default Description for the Leave Type. You can customize this",
        "leaves_per_year": 12.0,
        "weekends_between_leave": False,
        "holidays_between_leave": False,
        "accrual_enabled": True,
        "accrual_frequency": "monthly",
        "accrual_period": "No",
        "allowed_under_probation": False,
        "allowed_under_notice_period": False,
        "encashment_allowed": True,
        "max_encashment_days": 15,
        "carry_forward_allowed": True,
        "carry_forward_limit": 15,
        "max_leaves_per_month": 12.0,
        "continuous_leaves_allowed": 12,
        "negative_leaves_allowed": False,
        "future_dated_allowed": True,
        "future_dated_after_days": 0,
        "backdated_allowed": True,
        "backdated_up_to_days": 15,
        "next_year_till_month": "January",
    },
    {
        "name": LeaveTypeName.earned,
        "display_name": "Earned Leave",
        "description": "This is a Default Description for the Leave Type. You can customize this",
        "leaves_per_year": 12.0,
        "weekends_between_leave": False,
        "holidays_between_leave": False,
        "accrual_enabled": True,
        "accrual_frequency": "monthly",
        "accrual_period": "No",
        "allowed_under_probation": False,
        "allowed_under_notice_period": False,
        "encashment_allowed": True,
        "max_encashment_days": 15,
        "carry_forward_allowed": True,
        "carry_forward_limit": 15,
        "max_leaves_per_month": 12.0,
        "continuous_leaves_allowed": 12,
        "negative_leaves_allowed": False,
        "future_dated_allowed": True,
        "future_dated_after_days": 0,
        "backdated_allowed": True,
        "backdated_up_to_days": 15,
        "next_year_till_month": "January",
    },
]


async def seed_super_admin() -> None:
    async with SessionLocal() as session:
        repo = UserRepository(session)
        existing = await repo.get_by_email(settings.SUPER_ADMIN_EMAIL)
        if existing:
            logger.info("Super admin already exists: %s", existing.email)
            return

        user = await repo.create(
            name=settings.SUPER_ADMIN_NAME,
            email=settings.SUPER_ADMIN_EMAIL,
            hashed_password=hash_password(settings.SUPER_ADMIN_PASSWORD),
            role=UserRole.super_admin,
            is_active=True,
        )
        user.employee_id = f"SA{user.id:05d}"
        await session.commit()
        logger.warning(
            "✅ Super admin created → email=%s password=%s",
            settings.SUPER_ADMIN_EMAIL,
            settings.SUPER_ADMIN_PASSWORD,
        )


async def seed_leave_types() -> None:
    async with SessionLocal() as session:
        for cfg in DEFAULT_LEAVE_TYPES:
            existing = await session.execute(
                select(LeaveType).where(LeaveType.name == cfg["name"])
            )
            record = existing.scalar_one_or_none()

            if record:
                changed = False
                for key in ("continuous_leaves_allowed", "max_leaves_per_month"):
                    if getattr(record, key) != cfg[key]:
                        setattr(record, key, cfg[key])
                        changed = True
                if changed:
                    logger.info(
                        "Updated limits for leave type %s: max_per_month=%s continuous=%s",
                        cfg["name"].value,
                        cfg["max_leaves_per_month"],
                        cfg["continuous_leaves_allowed"],
                    )
                else:
                    logger.info("Leave type already exists: %s", cfg["name"].value)
                continue

            session.add(LeaveType(**cfg))
            logger.info("Seeded leave type: %s", cfg["name"].value)

        await session.commit()
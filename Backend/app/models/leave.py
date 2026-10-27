# from datetime import date, datetime
# from enum import Enum as PyEnum

# from sqlalchemy import (
#     Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func,
# )
# from sqlalchemy.dialects.mysql import BIGINT
# from sqlalchemy.orm import Mapped, mapped_column

# from app.db.base import Base


# class LeaveTypeName(str, PyEnum):
#     casual = "casual"
#     sick = "sick"
#     earned = "earned"


# class LeaveStatus(str, PyEnum):
#     pending = "pending"
#     approved = "approved"
#     rejected = "rejected"
#     cancelled = "cancelled"


# class LeaveType(Base):
#     __tablename__ = "leave_types"
#     __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

#     id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
#     name: Mapped[LeaveTypeName] = mapped_column(
#         Enum(LeaveTypeName, native_enum=False, length=20), unique=True, nullable=False
#     )
#     display_name: Mapped[str] = mapped_column(String(100), nullable=False)
#     description: Mapped[str | None] = mapped_column(Text, nullable=True)

#     leaves_per_year: Mapped[float] = mapped_column(Float, default=12.0, nullable=False)
#     weekends_between_leave: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
#     holidays_between_leave: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

#     accrual_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
#     accrual_frequency: Mapped[str | None] = mapped_column(String(20), default="monthly", nullable=True)
#     accrual_period: Mapped[str | None] = mapped_column(String(50), default="No", nullable=True)

#     allowed_under_probation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
#     allowed_under_notice_period: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

#     encashment_allowed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
#     max_encashment_days: Mapped[int] = mapped_column(Integer, default=15, nullable=False)

#     carry_forward_allowed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
#     carry_forward_limit: Mapped[int] = mapped_column(Integer, default=15, nullable=False)

#     max_leaves_per_month: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
#     continuous_leaves_allowed: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
#     negative_leaves_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

#     future_dated_allowed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
#     future_dated_after_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
#     backdated_allowed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
#     backdated_up_to_days: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
#     next_year_till_month: Mapped[str | None] = mapped_column(String(20), default="January", nullable=True)

#     is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
#     created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
#     )


# class LeaveApplication(Base):
#     __tablename__ = "leave_applications"
#     __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

#     id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
#     user_id: Mapped[int] = mapped_column(
#         BIGINT(unsigned=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
#     )
#     employee_id: Mapped[str | None] = mapped_column(String(20), index=True, nullable=True)
#     employee_name: Mapped[str | None] = mapped_column(String(150), nullable=True)

#     leave_type: Mapped[LeaveTypeName] = mapped_column(
#         Enum(LeaveTypeName, native_enum=False, length=20), index=True, nullable=False
#     )
#     from_date: Mapped[date] = mapped_column(Date, nullable=False)
#     to_date: Mapped[date] = mapped_column(Date, nullable=False)
#     total_days: Mapped[float] = mapped_column(Float, nullable=False)
#     reason: Mapped[str | None] = mapped_column(Text, nullable=True)

#     status: Mapped[LeaveStatus] = mapped_column(
#         Enum(LeaveStatus, native_enum=False, length=20),
#         default=LeaveStatus.pending, index=True, nullable=False,
#     )

#     reviewed_by_id: Mapped[int | None] = mapped_column(
#         BIGINT(unsigned=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
#     )
#     reviewed_by_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
#     reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
#     review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

#     applied_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
from datetime import date, datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func,
)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LeaveTypeName(str, PyEnum):
    casual = "casual"
    sick = "sick"
    earned = "earned"


class LeaveStatus(str, PyEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"


class LeaveType(Base):
    __tablename__ = "leave_types"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    name: Mapped[LeaveTypeName] = mapped_column(
        Enum(LeaveTypeName, native_enum=False, length=20), unique=True, nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    leaves_per_year: Mapped[float] = mapped_column(Float, default=12.0, nullable=False)
    weekends_between_leave: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    holidays_between_leave: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    accrual_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    accrual_frequency: Mapped[str | None] = mapped_column(String(20), default="monthly", nullable=True)
    accrual_period: Mapped[str | None] = mapped_column(String(50), default="No", nullable=True)

    allowed_under_probation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allowed_under_notice_period: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    encashment_allowed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_encashment_days: Mapped[int] = mapped_column(Integer, default=15, nullable=False)

    carry_forward_allowed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    carry_forward_limit: Mapped[int] = mapped_column(Integer, default=15, nullable=False)

    max_leaves_per_month: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    continuous_leaves_allowed: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    negative_leaves_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    future_dated_allowed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    future_dated_after_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    backdated_allowed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    backdated_up_to_days: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    next_year_till_month: Mapped[str | None] = mapped_column(String(20), default="January", nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )


class LeaveApplication(Base):
    __tablename__ = "leave_applications"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    employee_id: Mapped[str | None] = mapped_column(String(20), index=True, nullable=True)
    employee_name: Mapped[str | None] = mapped_column(String(150), nullable=True)

    leave_type: Mapped[LeaveTypeName] = mapped_column(
        Enum(LeaveTypeName, native_enum=False, length=20), index=True, nullable=False
    )
    from_date: Mapped[date] = mapped_column(Date, nullable=False)
    to_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_days: Mapped[float] = mapped_column(Float, nullable=False)

    half_day: Mapped[str | None] = mapped_column(String(30), nullable=True)

    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[LeaveStatus] = mapped_column(
        Enum(LeaveStatus, native_enum=False, length=20),
        default=LeaveStatus.pending, index=True, nullable=False,
    )

    reviewed_by_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_by_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    applied_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
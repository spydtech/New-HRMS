from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)

    user_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    employee_id: Mapped[str | None] = mapped_column(String(20), index=True, nullable=True)
    employee_name: Mapped[str | None] = mapped_column(String(150), nullable=True)

    punch_in: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    punch_out: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    production_hours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    production_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    production_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    break_hours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    break_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    break_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    working_hours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    working_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    working_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    overtime: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
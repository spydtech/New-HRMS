from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, String, Table, Text, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Association table for Event <-> Employee (User) Many-to-Many
event_employees = Table(
    "event_employees",
    Base.metadata,
    Column(
        "event_id",
        BIGINT(unsigned=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "user_id",
        BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
)

class Event(Base):
    __tablename__ = "events"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationship to assigned employees
    assigned_employees = relationship(
        "User", secondary=event_employees, lazy="selectin"
    )
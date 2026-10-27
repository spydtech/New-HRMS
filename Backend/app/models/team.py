from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, Text, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


team_members = Table(
    "team_members",
    Base.metadata,
    Column(
        "team_id",
        BIGINT(unsigned=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
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


class Team(Base):
    __tablename__ = "teams"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True
    )
    team_name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)

    lead_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    lead = relationship("User", foreign_keys=[lead_id], lazy="selectin")
    members = relationship("User", secondary=team_members, lazy="selectin")
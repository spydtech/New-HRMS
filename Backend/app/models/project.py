from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.mysql import BIGINT, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True
    )
    project_name: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    client_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("clients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    team_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    team_lead_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    project_priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Medium"
    )
    rate: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    rate_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="Active"
    )
    progress: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    project_image: Mapped[str | None] = mapped_column(LONGTEXT, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    client = relationship("Client", back_populates="projects", lazy="selectin")
    team = relationship("Team", lazy="selectin")
    team_lead = relationship("User", foreign_keys=[team_lead_id], lazy="selectin")
    activities = relationship(
        "ProjectActivity",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(ProjectActivity.created_at)",
    )
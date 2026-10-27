from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.mysql import BIGINT, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProjectActivity(Base):
    __tablename__ = "project_activities"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True
    )
    project_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    activity_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default="message"
    )
    attachments_json: Mapped[str | None] = mapped_column(LONGTEXT, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    project = relationship("Project", back_populates="activities")
    user = relationship("User", lazy="selectin")
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ActivityAuthorInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    email: str
    profileImage: str | None = Field(default=None, validation_alias="profile_image")
    designation: str | None = None


class ProjectActivityCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    content: str = Field(min_length=1, max_length=5000)
    activityType: str = Field(default="message", validation_alias="activityType")
    attachments: list[dict] | None = None
    progress: int | None = Field(default=None, ge=0, le=100)


class ProjectActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    projectId: int = Field(validation_alias="project_id")
    content: str
    activityType: str = Field(validation_alias="activity_type")
    attachments: list[dict] = []
    user: ActivityAuthorInfo | None = None
    createdAt: datetime = Field(validation_alias="created_at")
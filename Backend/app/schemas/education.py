from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EducationBase(BaseModel):
    degree: str | None = None
    institution: str | None = None
    university: str | None = None
    start_year: str | None = Field(default=None, alias="startYear")
    end_year: str | None = Field(default=None, alias="endYear")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class EducationCreate(EducationBase):
    pass


class EducationRead(EducationBase):
    id: int
    employee_id: str | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class EducationUpsert(BaseModel):
    """Accepts frontend payload: { degree, institution, university, startYear, endYear }."""

    degree: str | None = None
    institution: str | None = None
    university: str | None = None
    startYear: str | None = None
    endYear: str | None = None

    model_config = ConfigDict(extra="ignore")
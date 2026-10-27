from datetime import date, datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class EventEmployeeInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    email: str
    profileImage: str | None = Field(default=None, validation_alias="profile_image")
    designation: str | None = None


class EventBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    name: str = Field(
        validation_alias=AliasChoices("name", "title", "eventName")
    )
    event_date: date = Field(
        validation_alias=AliasChoices("date", "eventDate", "event_date")
    )
    description: str | None = None


class EventCreate(EventBase):
    # Optional list of employee IDs to assign
    employee_ids: list[int] = Field(
        default_factory=list, 
        validation_alias=AliasChoices("employeeIds", "employee_ids")
    )


class EventUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    name: str | None = None
    event_date: date | None = Field(
        default=None, validation_alias=AliasChoices("date", "eventDate", "event_date")
    )
    description: str | None = None
    employee_ids: list[int] | None = Field(
        default=None, validation_alias=AliasChoices("employeeIds", "employee_ids")
    )


class EventRead(EventBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    created_at: datetime
    assigned_employees: list[EventEmployeeInfo] = []
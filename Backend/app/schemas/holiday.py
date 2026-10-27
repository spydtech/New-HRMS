from datetime import date as DateType, datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class HolidayBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    day: str | None = None
    date: DateType | None = Field(
        default=None,
        validation_alias=AliasChoices("date", "holidayDate"),
    )
    holiday_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("holidayName", "holiday_name", "name"),
    )
    description: str | None = None
    holiday_type: str | None = Field(
        default="Public",
        validation_alias=AliasChoices("holidayType", "holiday_type", "type"),
    )


class HolidayCreate(HolidayBase):
    # Overriding a field in a subclass drops the parent's alias — repeat it.
    date: DateType = Field(
        validation_alias=AliasChoices("date", "holidayDate"),
    )
    holiday_name: str = Field(
        min_length=2,
        max_length=150,
        validation_alias=AliasChoices("holidayName", "holiday_name", "name"),
    )


class HolidayUpdate(HolidayBase):
    pass


class HolidayRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    day: str
    date: DateType
    holidayName: str = Field(validation_alias="holiday_name")
    holiday_name: str = Field(validation_alias="holiday_name")
    name: str = Field(validation_alias="holiday_name")
    description: str | None = None
    holidayType: str | None = Field(default=None, validation_alias="holiday_type")
    holiday_type: str | None = Field(default=None, validation_alias="holiday_type")
    type: str | None = Field(default=None, validation_alias="holiday_type")
    is_active: bool = True
    createdAt: datetime = Field(validation_alias="created_at")
    updatedAt: datetime = Field(validation_alias="updated_at")


def holiday_to_response(h) -> dict:
    return {
        "id": h.id,
        "day": h.day,
        "date": h.date,
        "holidayName": h.holiday_name,
        "holiday_name": h.holiday_name,
        "name": h.holiday_name,
        "description": h.description,
        "holidayType": h.holiday_type,
        "holiday_type": h.holiday_type,
        "type": h.holiday_type,
        "is_active": h.is_active,
        "createdAt": h.created_at,
        "updatedAt": h.updated_at,
    }
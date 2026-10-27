from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TimeParts(BaseModel):
    hours: int = 0
    minutes: int = 0
    seconds: int = 0


class AttendanceCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    employeeId: str | None = None
    employeeName: str | None = None
    punchIn: str | None = None
    punchOut: str | None = None

    production: TimeParts | None = None
    breakDuration: TimeParts | None = None

    productionHours: int = 0
    productionMinutes: int = 0
    productionSeconds: int = 0

    breakHours: int = 0
    breakMinutes: int = 0
    breakSeconds: int = 0

    workingHours: int = 0
    workingMinutes: int = 0
    workingSeconds: int = 0

    overtime: int = 0


class AttendanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    employeeId: str | None = Field(default=None, validation_alias="employee_id")
    employeeName: str | None = Field(default=None, validation_alias="employee_name")

    punchIn: datetime | None = Field(default=None, validation_alias="punch_in")
    punchOut: datetime | None = Field(default=None, validation_alias="punch_out")

    productionHours: int = Field(default=0, validation_alias="production_hours")
    productionMinutes: int = Field(default=0, validation_alias="production_minutes")
    productionSeconds: int = Field(default=0, validation_alias="production_seconds")

    breakHours: int = Field(default=0, validation_alias="break_hours")
    breakMinutes: int = Field(default=0, validation_alias="break_minutes")
    breakSeconds: int = Field(default=0, validation_alias="break_seconds")

    workingHours: int = Field(default=0, validation_alias="working_hours")
    workingMinutes: int = Field(default=0, validation_alias="working_minutes")
    workingSeconds: int = Field(default=0, validation_alias="working_seconds")

    overtime: int = 0


def attendance_to_response(a) -> dict:
    return {
        "id": a.id,
        "employeeId": a.employee_id,
        "employeeName": a.employee_name,
        "punchIn": a.punch_in,
        "punchOut": a.punch_out,
        "productionHours": a.production_hours,
        "productionMinutes": a.production_minutes,
        "productionSeconds": a.production_seconds,
        "breakHours": a.break_hours,
        "breakMinutes": a.break_minutes,
        "breakSeconds": a.break_seconds,
        "workingHours": a.working_hours,
        "workingMinutes": a.working_minutes,
        "workingSeconds": a.working_seconds,
        "overtime": a.overtime,
    }
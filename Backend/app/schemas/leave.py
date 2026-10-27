# from datetime import date, datetime

# from pydantic import BaseModel, ConfigDict, Field

# from app.models.leave import LeaveStatus, LeaveTypeName


# class LeaveTypeRead(BaseModel):
#     model_config = ConfigDict(from_attributes=True)

#     id: int
#     name: LeaveTypeName
#     display_name: str
#     description: str | None = None

#     leaves_per_year: float
#     weekends_between_leave: bool
#     holidays_between_leave: bool

#     accrual_enabled: bool
#     accrual_frequency: str | None
#     accrual_period: str | None

#     allowed_under_probation: bool
#     allowed_under_notice_period: bool

#     encashment_allowed: bool
#     max_encashment_days: int

#     carry_forward_allowed: bool
#     carry_forward_limit: int

#     max_leaves_per_month: float
#     continuous_leaves_allowed: int
#     negative_leaves_allowed: bool

#     future_dated_allowed: bool
#     future_dated_after_days: int
#     backdated_allowed: bool
#     backdated_up_to_days: int
#     next_year_till_month: str | None

#     is_active: bool


# class LeaveTypeUpdate(BaseModel):
#     model_config = ConfigDict(extra="ignore")

#     display_name: str | None = None
#     description: str | None = None
#     leaves_per_year: float | None = None
#     weekends_between_leave: bool | None = None
#     holidays_between_leave: bool | None = None
#     accrual_enabled: bool | None = None
#     accrual_frequency: str | None = None
#     accrual_period: str | None = None
#     allowed_under_probation: bool | None = None
#     allowed_under_notice_period: bool | None = None
#     encashment_allowed: bool | None = None
#     max_encashment_days: int | None = None
#     carry_forward_allowed: bool | None = None
#     carry_forward_limit: int | None = None
#     max_leaves_per_month: float | None = None
#     continuous_leaves_allowed: int | None = None
#     negative_leaves_allowed: bool | None = None
#     future_dated_allowed: bool | None = None
#     future_dated_after_days: int | None = None
#     backdated_allowed: bool | None = None
#     backdated_up_to_days: int | None = None
#     next_year_till_month: str | None = None


# class LeaveApplicationCreate(BaseModel):
#     leave_type: LeaveTypeName
#     from_date: date
#     to_date: date
#     reason: str | None = None


# class LeaveApplicationReview(BaseModel):
#     comment: str | None = None


# class LeaveApplicationRead(BaseModel):
#     model_config = ConfigDict(from_attributes=True, populate_by_name=True)

#     id: int
#     employeeId: str | None = Field(default=None, validation_alias="employee_id")
#     employeeName: str | None = Field(default=None, validation_alias="employee_name")

#     leaveType: LeaveTypeName = Field(validation_alias="leave_type")
#     fromDate: date = Field(validation_alias="from_date")
#     toDate: date = Field(validation_alias="to_date")
#     totalDays: float = Field(validation_alias="total_days")
#     reason: str | None = None
#     status: LeaveStatus

#     reviewedByName: str | None = Field(default=None, validation_alias="reviewed_by_name")
#     reviewedAt: datetime | None = Field(default=None, validation_alias="reviewed_at")
#     reviewComment: str | None = Field(default=None, validation_alias="review_comment")

#     appliedAt: datetime = Field(validation_alias="applied_at")


# def leave_to_response(a) -> dict:
#     return {
#         "id": a.id,
#         "employeeId": a.employee_id,
#         "employeeName": a.employee_name,
#         "leaveType": a.leave_type,
#         "fromDate": a.from_date,
#         "toDate": a.to_date,
#         "totalDays": a.total_days,
#         "reason": a.reason,
#         "status": a.status,
#         "reviewedByName": a.reviewed_by_name,
#         "reviewedAt": a.reviewed_at,
#         "reviewComment": a.review_comment,
#         "appliedAt": a.applied_at,
#     }


# class LeaveBalanceRead(BaseModel):
#     model_config = ConfigDict(populate_by_name=True)

#     employeeId: str | None = None
#     employeeName: str | None = None
#     casual: float = 0
#     sick: float = 0
#     earned: float = 0
#     compOff: float = 0
#     totalAllocated: float = 0
#     totalUsed: float = 0
#     totalPending: float = 0

from datetime import date, datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from app.models.leave import LeaveStatus, LeaveTypeName


class LeaveTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: LeaveTypeName
    display_name: str
    description: str | None = None
    leaves_per_year: float
    weekends_between_leave: bool
    holidays_between_leave: bool
    accrual_enabled: bool
    accrual_frequency: str | None
    accrual_period: str | None
    allowed_under_probation: bool
    allowed_under_notice_period: bool
    encashment_allowed: bool
    max_encashment_days: int
    carry_forward_allowed: bool
    carry_forward_limit: int
    max_leaves_per_month: float
    continuous_leaves_allowed: int
    negative_leaves_allowed: bool
    future_dated_allowed: bool
    future_dated_after_days: int
    backdated_allowed: bool
    backdated_up_to_days: int
    next_year_till_month: str | None
    is_active: bool


class LeaveTypeUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    display_name: str | None = None
    description: str | None = None
    leaves_per_year: float | None = None
    weekends_between_leave: bool | None = None
    holidays_between_leave: bool | None = None
    accrual_enabled: bool | None = None
    accrual_frequency: str | None = None
    accrual_period: str | None = None
    allowed_under_probation: bool | None = None
    allowed_under_notice_period: bool | None = None
    encashment_allowed: bool | None = None
    max_encashment_days: int | None = None
    carry_forward_allowed: bool | None = None
    carry_forward_limit: int | None = None
    max_leaves_per_month: float | None = None
    continuous_leaves_allowed: int | None = None
    negative_leaves_allowed: bool | None = None
    future_dated_allowed: bool | None = None
    future_dated_after_days: int | None = None
    backdated_allowed: bool | None = None
    backdated_up_to_days: int | None = None
    next_year_till_month: str | None = None


class LeaveApplicationCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    leave_type: LeaveTypeName = Field(validation_alias=AliasChoices("leaveType", "leave_type"))
    from_date: date = Field(validation_alias=AliasChoices("startdate", "from_date"))
    to_date: date = Field(validation_alias=AliasChoices("enddate", "to_date"))
    half_day: str | None = Field(default=None, validation_alias=AliasChoices("selecthalf", "half_day"))
    reason: str | None = None


class LeaveApplicationReview(BaseModel):
    comment: str | None = None


class LeaveApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    employeeId: str | None = Field(default=None, validation_alias="employee_id")
    employeeName: str | None = Field(default=None, validation_alias="employee_name")

    leaveType: LeaveTypeName = Field(validation_alias="leave_type")
    fromDate: date = Field(validation_alias="from_date")
    toDate: date = Field(validation_alias="to_date")
    totalDays: float = Field(validation_alias="total_days")
    halfDay: str | None = Field(default=None, validation_alias="half_day")
    reason: str | None = None
    status: LeaveStatus

    reviewedByName: str | None = Field(default=None, validation_alias="reviewed_by_name")
    reviewedAt: datetime | None = Field(default=None, validation_alias="reviewed_at")
    reviewComment: str | None = Field(default=None, validation_alias="review_comment")

    appliedAt: datetime = Field(validation_alias="applied_at")


def leave_to_response(a) -> dict:
    return {
        "id": a.id,
        "employeeId": a.employee_id,
        "employeeName": a.employee_name,
        "leaveType": a.leave_type,
        "fromDate": a.from_date,
        "toDate": a.to_date,
        "totalDays": a.total_days,
        "halfDay": a.half_day,
        "reason": a.reason,
        "status": a.status,
        "reviewedByName": a.reviewed_by_name,
        "reviewedAt": a.reviewed_at,
        "reviewComment": a.review_comment,
        "appliedAt": a.applied_at,
    }


class LeaveBalanceRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    employeeId: str | None = None
    employeeName: str | None = None

    # Available per type = allocated − used(approved) − pending
    casual: float = 0
    sick: float = 0
    earned: float = 0
    compOff: float = 0

    # Per-type breakdown
    casualAllocated: float = 0
    casualUsed: float = 0
    casualPending: float = 0
    casualRejected: float = 0

    sickAllocated: float = 0
    sickUsed: float = 0
    sickPending: float = 0
    sickRejected: float = 0

    earnedAllocated: float = 0
    earnedUsed: float = 0
    earnedPending: float = 0
    earnedRejected: float = 0

    totalAllocated: float = 0
    totalUsed: float = 0
    totalPending: float = 0
    totalRejected: float = 0
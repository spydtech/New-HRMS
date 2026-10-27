import re
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserRole

PASSWORD_RE = re.compile(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)")


class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: UserRole = UserRole.employee

    @field_validator("password")
    @classmethod
    def _check_password(cls, v: str) -> str:
        if not PASSWORD_RE.search(v):
            raise ValueError("Password must contain uppercase, lowercase and a number")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    email: EmailStr
    role: UserRole
    employee_id: str | None = None
    is_active: bool
    created_at: datetime

    employeeId: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    designation: str | None = None
    blood_group: str | None = None
    bloodGroup: str | None = None
    contact_no: str | None = None
    phoneNumber: str | None = None
    alternate_phone: str | None = None
    alternatePhoneNumber: str | None = None
    personal_mail_id: str | None = None
    personalEmail: str | None = None
    officialEmail: str | None = None
    date_of_joining: date | None = None
    joinDate: date | None = None
    date_of_birth: date | None = None
    dob: date | None = None
    pan_number: str | None = None
    panNumber: str | None = None
    aadhar_card_number: str | None = None
    aadharCardNumber: str | None = None
    profile_image: str | None = None
    profileImage: str | None = None


class RegisterResponse(BaseModel):
    success: bool = True
    message: str = "Registration successful"
    data: UserRead


class LoginResponse(BaseModel):
    success: bool = True
    token: str
    token_type: str = "bearer"
    user: UserRead


class ProfileUpdate(BaseModel):
    name: str | None = None
    personal_mail_id: str | None = None
    personalEmail: str | None = None
    contact_no: str | None = None
    phoneNumber: str | None = None
    alternate_phone: str | None = None
    alternatePhoneNumber: str | None = None
    blood_group: str | None = None
    bloodGroup: str | None = None
    date_of_birth: date | None = None
    dob: date | None = None
    designation: str | None = None
    pan_number: str | None = None
    panNumber: str | None = None
    aadhar_card_number: str | None = None
    aadharCardNumber: str | None = None
    profile_image: str | None = None
    profileImage: str | None = None
from datetime import date
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserRole


ROLE_ALIASES = {
    "hr": "hr_admin", "hradmin": "hr_admin", "hr_admin": "hr_admin",
    "superadmin": "super_admin", "super": "super_admin", "super_admin": "super_admin",
    "admin": "admin", "manager": "manager",
    "employee": "employee", "emp": "employee", "": "employee",
}


def _normalize_role(v: Any) -> UserRole:
    if isinstance(v, UserRole):
        return v
    if v is None:
        return UserRole.employee
    s = str(v).strip().lower().replace(" ", "_").replace("-", "_")
    s = ROLE_ALIASES.get(s, s)
    try:
        return UserRole(s)
    except ValueError:
        return UserRole.employee


class EmployeeRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int                                              # ✅ ADDED — numeric PK
    employeeId: str | None = None
    firstName: str = ""
    lastName: str = ""
    name: str = ""
    email: str = ""
    officialEmail: str = ""
    role: UserRole = UserRole.employee
    joinDate: date | None = None
    phoneNumber: str | None = None
    alternatePhoneNumber: str | None = None
    bloodGroup: str | None = None
    personalEmail: str | None = None
    dob: date | None = None
    designation: str | None = None
    panNumber: str | None = None
    aadharCardNumber: str | None = None
    profileImage: str | None = None
    isActive: bool = True

    # Legacy aliases (kept for backwards compatibility)
    ID: str | None = None
    Name: str = ""
    DOJ: date | None = None
    ContactNo: str | None = None
    BloodGroup: str | None = None
    PersonalMailID: str | None = None
    OfficialMailID: str = ""
    DOB: date | None = None
    Designation: str | None = None
    Role: UserRole = UserRole.employee
    PANNumber: str | None = None
    AadharCardNumber: str | None = None


class EmployeeCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    employee_id: str | None = Field(default=None, validation_alias=AliasChoices("employeeId", "ID"))
    first_name: str | None = Field(default=None, validation_alias=AliasChoices("firstName", "FirstName"))
    last_name: str | None = Field(default=None, validation_alias=AliasChoices("lastName", "LastName"))
    name: str | None = Field(default=None, validation_alias=AliasChoices("Name", "name"))
    email: EmailStr = Field(validation_alias=AliasChoices("email", "OfficialMailID", "Email", "officialEmail"))
    role: UserRole = Field(default=UserRole.employee, validation_alias=AliasChoices("role", "Role"))
    date_of_joining: date | None = Field(default=None, validation_alias=AliasChoices("joinDate", "DOJ", "dateOfJoining"))
    date_of_birth: date | None = Field(default=None, validation_alias=AliasChoices("dob", "DOB", "dateOfBirth"))
    contact_no: str | None = Field(default=None, validation_alias=AliasChoices("phoneNumber", "ContactNo"))
    alternate_phone: str | None = Field(default=None, validation_alias=AliasChoices("alternatePhone", "alternatePhoneNumber"))
    blood_group: str | None = Field(default=None, validation_alias=AliasChoices("bloodGroup", "BloodGroup"))
    personal_mail_id: str | None = Field(default=None, validation_alias=AliasChoices("personalEmail", "PersonalMailID"))
    designation: str | None = Field(default=None, validation_alias=AliasChoices("designation", "Designation"))
    pan_number: str | None = Field(default=None, validation_alias=AliasChoices("panNumber", "PANNumber"))
    aadhar_card_number: str | None = Field(default=None, validation_alias=AliasChoices("aadharCardNumber", "AadharCardNumber"))
    password: str | None = Field(default=None, min_length=6, max_length=128)

    @field_validator("role", mode="before")
    @classmethod
    def _clean_role(cls, v):
        return _normalize_role(v)

    @field_validator("date_of_joining", "date_of_birth", mode="before")
    @classmethod
    def _empty_date(cls, v):
        return None if v in ("", None) else v

    @field_validator("contact_no", "alternate_phone", "blood_group", "personal_mail_id",
                     "designation", "pan_number", "aadhar_card_number", mode="before")
    @classmethod
    def _empty_str(cls, v):
        return None if v == "" else v

    @property
    def resolved_name(self) -> str:
        if self.name and self.name.strip():
            return self.name.strip()
        parts = [p.strip() for p in [self.first_name, self.last_name] if p]
        return " ".join(parts).strip()


class EmployeeUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    first_name: str | None = Field(default=None, validation_alias=AliasChoices("firstName", "FirstName"))
    last_name: str | None = Field(default=None, validation_alias=AliasChoices("lastName", "LastName"))
    name: str | None = Field(default=None, validation_alias=AliasChoices("Name", "name"))
    email: EmailStr | None = Field(default=None, validation_alias=AliasChoices("email", "OfficialMailID", "officialEmail"))
    role: UserRole | None = Field(default=None, validation_alias=AliasChoices("role", "Role"))
    date_of_joining: date | None = Field(default=None, validation_alias=AliasChoices("joinDate", "DOJ"))
    date_of_birth: date | None = Field(default=None, validation_alias=AliasChoices("dob", "DOB"))
    contact_no: str | None = Field(default=None, validation_alias=AliasChoices("phoneNumber", "ContactNo"))
    alternate_phone: str | None = Field(default=None, validation_alias=AliasChoices("alternatePhone", "alternatePhoneNumber"))
    blood_group: str | None = Field(default=None, validation_alias=AliasChoices("bloodGroup", "BloodGroup"))
    personal_mail_id: str | None = Field(default=None, validation_alias=AliasChoices("personalEmail", "PersonalMailID"))
    designation: str | None = Field(default=None, validation_alias=AliasChoices("designation", "Designation"))
    pan_number: str | None = Field(default=None, validation_alias=AliasChoices("panNumber", "PANNumber"))
    aadhar_card_number: str | None = Field(default=None, validation_alias=AliasChoices("aadharCardNumber", "AadharCardNumber"))
    password: str | None = Field(default=None, min_length=6, max_length=128)

    @field_validator("role", mode="before")
    @classmethod
    def _clean_role(cls, v):
        return None if v in (None, "") else _normalize_role(v)

    @field_validator("date_of_joining", "date_of_birth", mode="before")
    @classmethod
    def _empty_date(cls, v):
        return None if v in ("", None) else v

    @field_validator("contact_no", "alternate_phone", "blood_group", "personal_mail_id",
                     "designation", "pan_number", "aadhar_card_number", mode="before")
    @classmethod
    def _empty_str(cls, v):
        return None if v == "" else v

    @property
    def resolved_name(self) -> str | None:
        if self.name and self.name.strip():
            return self.name.strip()
        parts = [p.strip() for p in [self.first_name, self.last_name] if p]
        return " ".join(parts).strip() or None


def user_to_response(user) -> dict:
    full = user.name or ""
    first, _, last = full.partition(" ")
    return {
        "id": user.id,                                   # ✅ ADDED — numeric PK
        "employeeId": user.employee_id,
        "firstName": first or "",
        "lastName": last or "",
        "name": full,
        "email": user.email,
        "officialEmail": user.email,
        "role": user.role,
        "joinDate": user.date_of_joining,
        "phoneNumber": user.contact_no,
        "alternatePhoneNumber": user.alternate_phone,
        "bloodGroup": user.blood_group,
        "personalEmail": user.personal_mail_id,
        "dob": user.date_of_birth,
        "designation": user.designation,
        "panNumber": user.pan_number,
        "aadharCardNumber": user.aadhar_card_number,
        "profileImage": user.profile_image,
        "isActive": user.is_active,
        # Legacy aliases
        "ID": user.employee_id,
        "Name": full,
        "DOJ": user.date_of_joining,
        "ContactNo": user.contact_no,
        "BloodGroup": user.blood_group,
        "PersonalMailID": user.personal_mail_id,
        "OfficialMailID": user.email,
        "DOB": user.date_of_birth,
        "Designation": user.designation,
        "Role": user.role,
        "PANNumber": user.pan_number,
        "AadharCardNumber": user.aadhar_card_number,
    }
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClientBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    mobile: str | None = None
    company: str | None = None
    designation: str | None = None
    status: str = "User"
    address: str | None = None
    notes: str | None = None
    profile_image: str | None = None
    is_active: bool = True


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    name: str | None = None
    email: EmailStr | None = None
    mobile: str | None = None
    company: str | None = None
    designation: str | None = None
    status: str | None = None
    address: str | None = None
    notes: str | None = None
    profile_image: str | None = None
    is_active: bool | None = None


class ClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    email: str
    mobile: str | None = None
    company: str | None = None
    designation: str | None = None
    role: str | None = Field(default=None, validation_alias="designation")
    status: str = "User"
    address: str | None = None
    notes: str | None = None
    profileImage: str | None = Field(default=None, validation_alias="profile_image")
    profile_image: str | None = None
    isActive: bool = Field(default=True, validation_alias="is_active")
    is_active: bool = True
    createdAt: datetime = Field(validation_alias="created_at")
    updatedAt: datetime = Field(validation_alias="updated_at")
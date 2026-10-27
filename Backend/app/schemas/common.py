from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str | None = None
    data: T | None = None


class MessageResponse(BaseModel):
    success: bool = True
    message: str
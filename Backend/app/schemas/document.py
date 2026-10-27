from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    employee_id: str | None = None
    employeeId: str | None = None
    id_type: str
    idType: str
    id_number: str | None = None
    idNumber: str | None = None
    file_path: str | None = None
    fileName: str | None = None
    image: str | None = None
    uploaded_at: datetime | None = None
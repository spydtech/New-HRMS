import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.exceptions import ForbiddenError, NotFoundError
from app.models.document import Document
from app.models.user import UserRole
from app.schemas.document import DocumentRead

router = APIRouter(prefix="/aadhar", tags=["documents"])

HR_ROLES = (UserRole.super_admin, UserRole.hr_admin, UserRole.admin)

UPLOAD_DIR = Path("uploads/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE_MB = 10


def _serialize(doc: Document) -> dict:
    return {
        "id": doc.id,
        "employee_id": doc.employee_id,
        "employeeId": doc.employee_id,
        "id_type": doc.id_type,
        "idType": doc.id_type,
        "id_number": doc.id_number,
        "idNumber": doc.id_number,
        "file_path": doc.file_path,
        "fileName": doc.file_name,
        "image": doc.file_name,
        "uploaded_at": doc.uploaded_at,
    }


@router.get("/get/{employee_id}", response_model=list[DocumentRead])
async def get_documents(employee_id: str, session: DbSession, current_user: CurrentUser):
    # self or HR
    if employee_id != current_user.employee_id and current_user.role not in HR_ROLES:
        raise ForbiddenError("Not enough permissions")

    result = await session.execute(
        select(Document).where(Document.employee_id == employee_id).order_by(Document.id)
    )
    return [_serialize(d) for d in result.scalars().all()]


@router.post("/save", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def save_document(
    session: DbSession,
    current_user: CurrentUser,
    idType: str = Form(...),
    idNumber: str = Form(...),
    employeeId: str = Form(...),
    file: UploadFile | None = File(None),
):
    if employeeId != current_user.employee_id and current_user.role not in HR_ROLES:
        raise ForbiddenError("Not enough permissions")

    file_path = None
    file_name = None
    if file is not None:
        content = await file.read()
        if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(413, f"File exceeds {MAX_FILE_SIZE_MB}MB limit")
        ext = Path(file.filename).suffix
        unique = f"{uuid.uuid4().hex}{ext}"
        dest = UPLOAD_DIR / unique
        dest.write_bytes(content)
        file_path = f"/uploads/documents/{unique}"
        file_name = file.filename

    doc = Document(
        user_id=current_user.id,
        employee_id=employeeId,
        id_type=idType,
        id_number=idNumber,
        file_path=file_path,
        file_name=file_name,
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return _serialize(doc)


@router.put("/update", response_model=DocumentRead)
async def update_document(
    session: DbSession,
    current_user: CurrentUser,
    idType: str = Form(...),
    idNumber: str = Form(...),
    employeeId: str = Form(...),
    file: UploadFile | None = File(None),
):
    if employeeId != current_user.employee_id and current_user.role not in HR_ROLES:
        raise ForbiddenError("Not enough permissions")

    result = await session.execute(
        select(Document).where(
            Document.employee_id == employeeId, Document.id_type == idType
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise NotFoundError("Document not found")

    doc.id_number = idNumber
    if file is not None:
        content = await file.read()
        if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(413, f"File exceeds {MAX_FILE_SIZE_MB}MB limit")
        ext = Path(file.filename).suffix
        unique = f"{uuid.uuid4().hex}{ext}"
        dest = UPLOAD_DIR / unique
        dest.write_bytes(content)
        doc.file_path = f"/uploads/documents/{unique}"
        doc.file_name = file.filename

    await session.commit()
    await session.refresh(doc)
    return _serialize(doc)


@router.delete("/{employee_id}/{id_type}")
async def delete_document(
    employee_id: str,
    id_type: str,
    session: DbSession,
    current_user: CurrentUser,
):
    if employee_id != current_user.employee_id and current_user.role not in HR_ROLES:
        raise ForbiddenError("Not enough permissions")

    result = await session.execute(
        select(Document).where(
            Document.employee_id == employee_id, Document.id_type == id_type
        )
    )
    rows = list(result.scalars().all())
    if not rows:
        raise NotFoundError("Document not found")

    for row in rows:
        if row.file_path:
            disk = Path(row.file_path.lstrip("/"))
            if disk.exists():
                try:
                    disk.unlink()
                except OSError:
                    pass
        await session.delete(row)

    await session.commit()
    return {"success": True, "message": "Document deleted"}
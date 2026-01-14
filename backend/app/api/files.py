import json
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File as FileParam, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.db.models import AuditLog, File, FileContext, User
from app.db.session import SessionLocal
from app.schemas.files import BatchDownloadRequest, FileListResponse, FileResponse as FileSchema
from app.services.storage import save_upload, stream_file


router = APIRouter(prefix="/files", tags=["files"], dependencies=[Depends(get_current_user)])


def create_audit(actor_id: str | None, action: str, file_id: str | None, meta: dict | None) -> None:
    db = SessionLocal()
    try:
        db.add(AuditLog(actor_id=actor_id, action=action, file_id=file_id, meta=meta))
        db.commit()
    finally:
        db.close()


@router.get("", response_model=FileListResponse)
def list_files(
    q: Optional[str] = Query(default=None),
    doc_type: Optional[str] = Query(default=None),
    project_code: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> FileListResponse:
    query = db.query(File).filter(File.is_active.is_(True))
    if q:
        query = query.filter(File.original_name.ilike(f"%{q}%"))
    if doc_type:
        doc_type = doc_type.lower().lstrip(".")
        query = query.filter(func.lower(File.original_name).like(f"%.{doc_type}"))
    if project_code:
        query = query.join(FileContext).filter(FileContext.project_code == project_code)

    total = query.count()
    items = (
        query.order_by(File.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return FileListResponse(items=items, page=page, page_size=page_size, total=total)


@router.post("/upload", response_model=FileSchema)
def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = FileParam(...),
    project_code: Optional[str] = Form(default=None),
    experiment_id: Optional[str] = Form(default=None),
    step_name: Optional[str] = Form(default=None),
    tags: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileSchema:
    stored_path, size, checksum = save_upload(file)

    record = File(
        original_name=file.filename,
        stored_path=stored_path,
        file_size=size,
        mime_type=file.content_type,
        checksum_sha256=checksum,
        uploader_id=current_user.id,
    )
    db.add(record)
    db.flush()

    if project_code or experiment_id or step_name or tags:
        parsed_tags = None
        if tags:
            try:
                parsed_tags = json.loads(tags)
            except json.JSONDecodeError:
                parsed_tags = {"raw": tags}
        db.add(
            FileContext(
                file_id=record.id,
                project_code=project_code,
                experiment_id=experiment_id,
                step_name=step_name,
                tags=parsed_tags,
            )
        )

    db.commit()

    background_tasks.add_task(
        create_audit,
        str(current_user.id),
        "UPLOAD",
        str(record.id),
        {"original_name": record.original_name, "size": record.file_size},
    )

    return record


@router.get("/{file_id}", response_model=FileSchema)
def get_file(file_id: str, db: Session = Depends(get_db)) -> FileSchema:
    record = db.query(File).filter(File.id == file_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return record


@router.get("/{file_id}/download")
def download_file(
    file_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    record = db.query(File).filter(File.id == file_id, File.is_active.is_(True)).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if not os.path.exists(record.stored_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file missing")

    background_tasks.add_task(
        create_audit,
        str(current_user.id),
        "DOWNLOAD",
        str(record.id),
        {"original_name": record.original_name},
    )

    headers = {"Content-Disposition": f"attachment; filename=\"{record.original_name}\""}
    return StreamingResponse(stream_file(record.stored_path), media_type=record.mime_type, headers=headers)


@router.post("/batch-download")
def batch_download(
    payload: BatchDownloadRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    records = (
        db.query(File).filter(File.id.in_(payload.file_ids), File.is_active.is_(True)).all()
    )
    if not records:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Files not found")

    temp_dir = Path("/tmp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    zip_path = temp_dir / f"batch-{current_user.id}.zip"

    from zipfile import ZipFile, ZIP_DEFLATED

    used_names: set[str] = set()
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zip_handle:
        for record in records:
            if not os.path.exists(record.stored_path):
                continue
            name = record.original_name
            if name in used_names:
                name = f"{record.id}-{name}"
            used_names.add(name)
            zip_handle.write(record.stored_path, arcname=name)

    background_tasks.add_task(
        create_audit,
        str(current_user.id),
        "DOWNLOAD_BATCH",
        None,
        {"file_ids": [str(item.id) for item in records]},
    )

    return FileResponse(path=zip_path, filename="batch-download.zip", media_type="application/zip")


@router.post("/{file_id}/lock")
def lock_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileSchema:
    record = db.query(File).filter(File.id == file_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if record.lock_status == "LOCKED" and str(record.locked_by) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="File already locked")
    record.lock_status = "LOCKED"
    record.locked_by = current_user.id
    db.commit()
    db.refresh(record)
    return record


@router.post("/{file_id}/unlock")
def unlock_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileSchema:
    record = db.query(File).filter(File.id == file_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if record.lock_status == "UNLOCKED":
        return record
    if str(record.locked_by) != str(current_user.id) and current_user.role.lower() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    record.lock_status = "UNLOCKED"
    record.locked_by = None
    db.commit()
    db.refresh(record)
    return record

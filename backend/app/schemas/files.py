from datetime import date, datetime
from pydantic import BaseModel


class FileResponse(BaseModel):
    id: str
    original_name: str
    stored_path: str
    file_size: int
    mime_type: str | None
    checksum_sha256: str
    version: int
    parent_file_id: str | None
    is_latest: bool
    lock_status: str
    locked_by: str | None
    uploader_id: str
    created_at: datetime
    expiry_date: date | None
    is_active: bool

    class Config:
        orm_mode = True


class FileListResponse(BaseModel):
    items: list[FileResponse]
    page: int
    page_size: int
    total: int


class BatchDownloadRequest(BaseModel):
    file_ids: list[str]

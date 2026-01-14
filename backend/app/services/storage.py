import hashlib
import os
from pathlib import Path
from typing import Generator

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings


settings = get_settings()


def allowed_extension(filename: str) -> bool:
    allowed = {ext.strip().lower() for ext in settings.allowed_extensions.split(",") if ext}
    ext = Path(filename).suffix.lower().lstrip(".")
    return ext in allowed


def ensure_storage_path() -> Path:
    path = Path(settings.storage_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_upload(file: UploadFile) -> tuple[str, int, str]:
    if not allowed_extension(file.filename or ""):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File extension not allowed")

    storage_dir = ensure_storage_path()
    target_name = f"{hashlib.sha256(os.urandom(32)).hexdigest()}"
    target_path = storage_dir / target_name

    hasher = hashlib.sha256()
    size = 0
    with target_path.open("wb") as target:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > settings.max_upload_size_bytes:
                target.close()
                target_path.unlink(missing_ok=True)
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")
            hasher.update(chunk)
            target.write(chunk)

    return str(target_path), size, hasher.hexdigest()


def stream_file(path: str) -> Generator[bytes, None, None]:
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            yield chunk

import uuid

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    dept = Column(String(200))
    role = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_name = Column(String(500), nullable=False)
    stored_path = Column(String(1000), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(200))
    checksum_sha256 = Column(String(64), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    parent_file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"))
    is_latest = Column(Boolean, nullable=False, default=True)
    lock_status = Column(
        Enum("UNLOCKED", "LOCKED", name="lock_status_enum"),
        nullable=False,
        default="UNLOCKED",
    )
    locked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    uploader_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    expiry_date = Column(Date)
    is_active = Column(Boolean, nullable=False, default=True)

    uploader = relationship("User", foreign_keys=[uploader_id])


class FileContext(Base):
    __tablename__ = "file_contexts"

    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"), primary_key=True)
    project_code = Column(String(200))
    experiment_id = Column(String(200))
    step_name = Column(String(200))
    tags = Column(JSONB)

    file = relationship("File")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"))
    meta = Column(JSONB)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    actor = relationship("User")
    file = relationship("File")

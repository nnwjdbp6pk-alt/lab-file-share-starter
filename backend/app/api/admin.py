from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.db.models import AuditLog
from app.schemas.audit import AuditLogResponse


router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/audit-logs", response_model=list[AuditLogResponse])
def list_audit_logs(db: Session = Depends(get_db)) -> list[AuditLogResponse]:
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(200).all()

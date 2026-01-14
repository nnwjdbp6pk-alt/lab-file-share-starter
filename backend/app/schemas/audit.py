from datetime import datetime
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: str
    actor_id: str | None
    action: str
    file_id: str | None
    meta: dict | None
    created_at: datetime

    class Config:
        orm_mode = True

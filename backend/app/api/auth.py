from datetime import timedelta
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_db
from app.core.security import create_access_token, verify_password
from app.db.models import User
from app.schemas.auth import LoginRequest, TokenResponse, UserInfo


router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def load_local_users() -> list[dict]:
    if not settings.default_users:
        return []
    try:
        data = json.loads(settings.default_users)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def verify_local_password(entry: dict, password: str) -> bool:
    password_hash = entry.get("password_hash")
    if password_hash:
        return verify_password(password, password_hash)
    return entry.get("password") == password


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    local_users = load_local_users()
    entry = next((item for item in local_users if item.get("username") == payload.username), None)
    if not entry or not verify_local_password(entry, payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not provisioned")

    expires = timedelta(minutes=settings.access_token_expire_minutes)
    token = create_access_token({"sub": str(user.id), "role": user.role}, expires)

    return TokenResponse(
        access_token=token,
        token_type="Bearer",
        expires_in=int(expires.total_seconds()),
        user=UserInfo(id=str(user.id), name=user.display_name, role=user.role),
    )

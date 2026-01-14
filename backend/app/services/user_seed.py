import json
from typing import Iterable

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import User


settings = get_settings()


def parse_default_users(raw: str) -> Iterable[dict]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def seed_default_users(db: Session) -> None:
    users = parse_default_users(settings.default_users)
    for entry in users:
        username = entry.get("username")
        password = entry.get("password")
        role = entry.get("role", "viewer")
        display_name = entry.get("display_name", username)
        if not username or not password:
            continue
        exists = db.query(User).filter(User.username == username).first()
        if exists:
            continue
        db.add(
            User(
                username=username,
                display_name=display_name,
                role=role,
                dept=entry.get("dept"),
            )
        )
    if users:
        db.commit()

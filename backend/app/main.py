from fastapi import FastAPI

from app.api import admin, auth, files
from app.db.session import SessionLocal
from app.services.user_seed import seed_default_users


app = FastAPI(title="Lab File Share API")

app.include_router(auth.router, prefix="/api")
app.include_router(files.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.on_event("startup")
def startup() -> None:
    db = SessionLocal()
    try:
        seed_default_users(db)
    finally:
        db.close()

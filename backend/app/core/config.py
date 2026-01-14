from functools import lru_cache
import os
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    database_url: str = Field(
        "postgresql://lab:lab@localhost:5432/labfiles", env="DATABASE_URL"
    )
    jwt_secret: str = Field("change-me", env="JWT_SECRET")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(60 * 8, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    storage_path: str = Field("./storage", env="STORAGE_PATH")
    max_upload_size_bytes: int = Field(50 * 1024 * 1024, env="MAX_UPLOAD_SIZE_BYTES")
    allowed_extensions: str = Field("pdf,docx,xlsx,pptx,png,jpg,jpeg", env="ALLOWED_EXTENSIONS")
    default_users: str = Field("", env="DEFAULT_USERS")

    class Config:
        env_file = os.getenv("ENV_FILE", ".env")
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()

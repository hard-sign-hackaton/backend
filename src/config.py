from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "DisplayAPP"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres-db:5432/KPOStudyTrackerDB"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    PASSWORD_SALT: str = "salt"

    class Config:
        env_file = ".env"

settings = Settings()
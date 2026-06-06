from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "DisplayAPP"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres-db:5432/DisplayDB"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    PASSWORD_SALT: str = "salt"
    API_KEY : str = "api_key"
    API_URL: str = "https://hck-api.unicorn.icu"
    MAX_RETRIES: int = 3
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
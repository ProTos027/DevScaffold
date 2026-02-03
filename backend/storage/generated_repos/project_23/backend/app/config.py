import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "FastAPI User Management"
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-for-dev-only-change-me-in-prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()

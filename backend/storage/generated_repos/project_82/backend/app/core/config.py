from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Todo App"
    VERSION: str = "1.0.0"
    SECRET_KEY: str = "supersecretkey" # CHANGE THIS IN PRODUCTION
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///./sql_app.db"

    # Pydantic-settings config
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
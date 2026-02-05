from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Todo App"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "A simple Todo application with user authentication."
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./sql_app.db"
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_REPLACE_ME"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
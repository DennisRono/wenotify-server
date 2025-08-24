import os
import pathlib
import secrets
from pydantic import AnyHttpUrl, field_validator
from typing import Any, Dict, List, Optional, Union, ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

DOTENV = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv()

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "WenotiFy Kenya"
    PROJECT_DESCRIPTION: str = (
        "WenotiFy Kenya"
    )
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"

    @field_validator("API_V1_STR", mode="before")
    @classmethod
    def normalize_api_path(cls, v: str) -> str:
        if v.startswith("C:/Program Files/Git"):
            return v.replace("C:/Program Files/Git", "")
        return v
    
    DEBUG: bool = True

    APP_HOME: ClassVar[pathlib.Path] = pathlib.Path(pathlib.Path(__file__).parent.parent)

    # Security Settings
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # CORS Settings
    CORS_ORIGINS: List[AnyHttpUrl] = []

    # Database Settings
    POSTGRES_SERVER: str = os.environ.get(
        "POSTGRES_SERVER", "localhost"
    )
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.environ.get(
        "POSTGRES_PASSWORD", "postgres"
    )
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "wenotify")
    SQLALCHEMY_DATABASE_URI: Optional[str] = (
        f"postgresql+asyncpg://{os.environ.get('POSTGRES_USER', 'postgres')}:{os.environ.get('POSTGRES_PASSWORD', 'postgres')}@{os.environ.get('POSTGRES_SERVER', 'localhost')}/{os.environ.get('POSTGRES_DB', 'wenotify')}"
    )

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return f"postgresql+asyncpg://{values.data.get('POSTGRES_USER')}:{values.data.get('POSTGRES_PASSWORD')}@{values.data.get('POSTGRES_SERVER')}/{values.data.get('POSTGRES_DB') or ''}"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT_LIMIT: int = 100
    RATE_LIMIT_DEFAULT_PERIOD: int = 60  # seconds

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()

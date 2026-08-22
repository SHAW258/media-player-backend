import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings(BaseSettings):
    APP_NAME: str = "Media Player API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = 8000
    
    # Database Settings
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "root")
    DB_NAME: str = os.getenv("DB_NAME", "mediaplayer_db")
    DB_SSL_CA: str | None = os.getenv(
        "DB_SSL_CA",
        str(BASE_DIR / "isrgrootx1.pem") if (BASE_DIR / "isrgrootx1.pem").exists() else None
    )
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', 'root')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', 3306)}/{os.getenv('DB_NAME', 'mediaplayer_db')}"
    )
    
    # JWT Security Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "mediaplayer_super_secret_jwt_key_development_2026")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))
    
    # Upload and Static Directories
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    STATIC_DIR: Path = BASE_DIR / "static"
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", 50))
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    
    class Config:
        case_sensitive = True
        extra = "ignore"

settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
(settings.UPLOAD_DIR / "audio").mkdir(parents=True, exist_ok=True)
(settings.UPLOAD_DIR / "covers").mkdir(parents=True, exist_ok=True)
(settings.STATIC_DIR / "audio").mkdir(parents=True, exist_ok=True)
(settings.STATIC_DIR / "images").mkdir(parents=True, exist_ok=True)

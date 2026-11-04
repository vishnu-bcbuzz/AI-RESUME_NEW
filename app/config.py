"""Application configuration module for FUTRSEC AI Resume Engine.

Safely loads configuration from environment variables and .env file.
Ensures sensitive credentials are never exposed in logs or representations.
"""

from pathlib import Path
from typing import List, Set
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Central application settings loaded from environment or .env."""

    # Application
    APP_NAME: str = "FUTRSEC AI Resume Engine"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = Field(..., description="Neon PostgreSQL connection URL")
    DB_POOL_MIN_SIZE: int = 2
    DB_POOL_MAX_SIZE: int = 10
    DB_CONNECT_TIMEOUT_SEC: float = 10.0

    # Business Rules
    SCORE_THRESHOLD: float = 80.0
    POST_IMPROVEMENT_THRESHOLD: float = 80.0
    MAX_IMPROVEMENT_ATTEMPTS: int = 3
    NON_COMPUTING_EDUCATION_DEDUCTION: float = 3.0
    ENABLE_NON_COMPUTING_EDUCATION_DEDUCTION: bool = True

    # Resume Upload
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    PROJECT_PLANS_DIR: Path = BASE_DIR / "uploads" / "generated" / "project_plans"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: Set[str] = {"pdf", "docx"}

    # Security & CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # Stage 1: Google Gemini API Resume Analysis Configuration (Hosted AI)
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    GEMINI_TIMEOUT_SEC: float = 60.0
    GEMINI_MAX_RETRIES: int = 3

    # Stage 2: OpenAI GPT API Resume Creation & Optimization Configuration
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TIMEOUT_SEC: float = 60.0
    OPENAI_MAX_RETRIES: int = 2

    # Templates & Output
    TEMPLATES_STORAGE_DIR: Path = BASE_DIR / "app" / "reports" / "storage"
    OUTPUT_DIR: Path = BASE_DIR / "uploads" / "generated"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def effective_gemini_key(self) -> str | None:
        import os
        return self.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")

    def is_gemini_configured(self) -> bool:
        return bool(self.effective_gemini_key)

    @property
    def effective_openai_key(self) -> str | None:
        import os
        return self.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")

    def is_openai_configured(self) -> bool:
        return bool(self.effective_openai_key)

    def is_ai_configured(self) -> bool:
        return self.is_openai_configured()

    def safe_summary(self) -> dict:
        """Returns safe configuration summary without credentials."""
        return {
            "app_name": self.APP_NAME,
            "version": self.APP_VERSION,
            "environment": self.ENVIRONMENT,
            "score_threshold": self.SCORE_THRESHOLD,
            "post_improvement_threshold": self.POST_IMPROVEMENT_THRESHOLD,
            "max_improvement_attempts": self.MAX_IMPROVEMENT_ATTEMPTS,
            "max_upload_size_mb": self.MAX_UPLOAD_SIZE_MB,
            "allowed_extensions": list(self.ALLOWED_EXTENSIONS),
            "stage1_analysis_provider": "Google Gemini API",
            "stage1_model": self.GEMINI_MODEL,
            "stage1_configured": self.is_gemini_configured(),
            "stage2_creation_provider": "OpenAI GPT",
            "stage2_model": self.OPENAI_MODEL,
            "stage2_configured": self.is_openai_configured(),
            "database_connected": bool(self.DATABASE_URL),
        }


settings = Settings()

# Ensure required runtime directories exist safely
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.TEMPLATES_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
settings.PROJECT_PLANS_DIR.mkdir(parents=True, exist_ok=True)

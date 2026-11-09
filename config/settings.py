"""
TenderFit - Application Configuration
Loads environment variables and exposes typed settings across backend, automation, and frontend.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # App
    APP_NAME: str = "TenderFit"
    APP_TAGLINE: str = "Find. Match. Win."
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/tenderfit_db"
    SQLITE_FALLBACK_URL: str = f"sqlite:///{BASE_DIR / 'tenderfit.db'}"

    # Backend API
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_BASE_URL: str = "http://127.0.0.1:8000"

    # Storage Paths
    COMPANY_DOCS_DIR: Path = BASE_DIR / "documents" / "company_documents"
    TENDER_DOCS_DIR: Path = BASE_DIR / "documents" / "tender_documents"
    REPORTS_DIR: Path = BASE_DIR / "reports"

    # Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Playwright Browser Automation
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_TIMEOUT: int = 30000

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# Ensure directories exist
settings.COMPANY_DOCS_DIR.mkdir(parents=True, exist_ok=True)
settings.TENDER_DOCS_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)


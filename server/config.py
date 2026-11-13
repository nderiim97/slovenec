"""Runtime configuration for the Slovenec portal."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(__file__).resolve().parent

try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:  # pragma: no cover - optional dependency
    pass


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _database_url() -> str:
    url = os.getenv(
        "DATABASE_URL", "sqlite:///" + (DATA_DIR / "slovenec.db").as_posix()
    )
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://") :]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


class Settings:
    app_name: str = "Slovenec"
    environment: str = os.getenv("APP_ENV", "development")

    secret_key: str = os.getenv("SECRET_KEY", "dev-only-change-me-please")
    session_days: int = int(os.getenv("SESSION_DAYS", "7"))
    trust_proxy: bool = _bool(
        os.getenv("TRUST_PROXY"), default=environment == "production"
    )

    database_url: str = _database_url()

    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@slovenec.local")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "slovenec123")

    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip(
        "/"
    )
    allowed_origins: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000"
        ).split(",")
        if origin.strip()
    ]

    site_name: str = os.getenv("SITE_NAME", "Slovenec")
    site_tagline: str = os.getenv("SITE_TAGLINE", "Slovenske novice, brez šuma")
    site_email: str = os.getenv("SITE_EMAIL", "urednistvo@slovenec.local")
    site_city: str = os.getenv("SITE_CITY", "Ljubljana")


settings = Settings()

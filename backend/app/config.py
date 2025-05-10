from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # Google OAuth settings
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL: str = "https://www.googleapis.com/oauth2/v1/userinfo"
    GOOGLE_CERTS_URL: str = "https://www.googleapis.com/oauth2/v3/certs"

    # App settings
    APP_NAME: str = "Google OAuth Demo"
    APP_ENV: str = "development"
    BASE_URL: Optional[str] = None
    FRONTEND_URL: Optional[str] = None
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v

    # JWT settings
    JWT_SECRET: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 15

    # Cookie settings
    COOKIE_DOMAIN: str = "localhost"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"
    COOKIE_MAX_AGE: int = 60 * 60 * 24 * 30  # 30 days

    # Database
    DATABASE_URL: Optional[str] = None

    # Encryption
    ENCRYPTION_KEY: Optional[str] = None

    # GCP Secret Manager (Optional, for production)
    GCP_PROJECT_ID: Optional[str] = None
    SECRET_MANAGER_PREFIX: Optional[str] = None


# Production setup for Secret Manager
def get_secret(secret_name: str) -> str:
    """Get secrets from GCP Secret Manager in production"""
    if settings.APP_ENV != "production" or not settings.GCP_PROJECT_ID:
        return None

    from google.cloud import secretmanager

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{settings.GCP_PROJECT_ID}/secrets/{settings.SECRET_MANAGER_PREFIX}-{secret_name}/versions/latest"

    try:
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error fetching secret {secret_name}: {e}")
        return None


# Load settings
settings = Settings()

# Override with Secret Manager values in production if available
if settings.APP_ENV == "production" and settings.GCP_PROJECT_ID:
    for field in [
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "JWT_SECRET",
        "ENCRYPTION_KEY",
    ]:
        secret_value = get_secret(field.lower())
        if secret_value:
            setattr(settings, field, secret_value)

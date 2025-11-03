# configs/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os


class Settings(BaseSettings):
    # --- Supabase ---
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_SERVICE_KEY: str = Field(..., description="Supabase service key")
    VOICE_STORAGE_BUCKET: str = Field("voice_samples", description="Supabase bucket name")

    # --- Redis / Celery ---
    REDIS_URL: str = Field("redis://localhost:6379/0", description="Redis connection URL")

    # --- Picovoice keys ---
    RHINO_ACCESS_KEY: str = Field(..., description="Picovoice Rhino Access Key")
    PORCUPINE_ACCESS_KEY: str = Field(..., description="Picovoice Porcupine Access Key")

    RHINO_CONTEXT_PATH: str = Field(..., description="Path to Rhino context file (.rhn)")
    PORCUPINE_KEYWORD_PATH: str = Field(..., description="Path to Porcupine keyword file (.ppn)")

    # --- Voice verification ---
    VOICE_MATCH_THRESHOLD: float = Field(0.75, description="Cosine similarity threshold for match")
    VOICE_REFERENCE_DIR: str = Field("reference_voices", description="Local directory for reference samples")

    # --- Storage paths ---
    TEMP_DIR: str = Field(default_factory=lambda: os.path.join(os.getcwd(), "tmp"))

    # --- Email setup ---
    ADMIN_EMAIL: str | None = None
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASS: str | None = None

    # --- Testing fallback ---
    TEST_EMAIL: str = "test@example.com"

    # --- Celery settings ---
    CELERY_BROKER_URL: str = Field(default_factory=lambda: "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default_factory=lambda: "redis://localhost:6379/0")

    # --- .env file support ---
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
